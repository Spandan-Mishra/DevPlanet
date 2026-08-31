package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/spandev/devplanet/api/internal/cache"
	"github.com/spandev/devplanet/api/internal/config"
	"github.com/spandev/devplanet/api/internal/github"
	"github.com/spandev/devplanet/api/internal/handler"
	"github.com/spandev/devplanet/api/internal/queue"
	"github.com/spandev/devplanet/api/internal/store"
	"github.com/spandev/devplanet/api/internal/worker"
)

func main() {
	cfg := config.Load()

	// Root context for app lifecycle
	appCtx, appCancel := context.WithCancel(context.Background())
	defer appCancel()

	// Initialize Redis Store (Cache & Task Queue)
	redisClient, err := store.NewRedisClient(cfg.RedisURL)
	if err != nil {
		log.Printf("[WARN] Redis connection failed (%v). Starting with degraded cache/queue.\n", err)
	} else {
		log.Println("[INFO] Successfully connected to Redis.")
		defer redisClient.Close()
	}

	appCache := cache.NewRedisCache(redisClient, "devplanet")
	taskQueue := queue.NewTaskQueue(redisClient, "queue:planet_tasks")
	ghClient := github.NewClient(cfg.GitHubToken)

	// Start Background Worker Pool
	if redisClient != nil {
		planetWorker := worker.NewPlanetWorker(taskQueue, appCache, ghClient)
		go planetWorker.Start(appCtx)
	}

	// Initialize HTTP Handlers
	planetHandler := handler.NewPlanetHandler(appCache, taskQueue, ghClient)
	jobHandler := handler.NewJobHandler(taskQueue)

	mux := http.NewServeMux()

	// Health check
	mux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte(`{"status":"ok","service":"devplanet-api"}`))
	})

	// Planet retrieval & generation routes
	mux.HandleFunc("/api/v1/planet/", planetHandler.HandlePlanet)

	// Job polling routes
	mux.HandleFunc("/api/v1/jobs/", jobHandler.HandleGetJob)

	server := &http.Server{
		Addr:         fmt.Sprintf(":%d", cfg.Port),
		Handler:      mux,
		ReadTimeout:  15 * time.Second,
		WriteTimeout: 15 * time.Second,
		IdleTimeout:  60 * time.Second,
	}

	// Server run context for graceful shutdown
	serverCtx, serverStopCtx := context.WithCancel(context.Background())

	// Listen for syscall signals for graceful shutdown
	sig := make(chan os.Signal, 1)
	signal.Notify(sig, syscall.SIGHUP, syscall.SIGINT, syscall.SIGTERM, syscall.SIGQUIT)
	go func() {
		<-sig
		log.Println("Received termination signal, shutting down gracefully...")

		// Stop background workers
		appCancel()

		// Allow active requests 10 seconds to finish
		shutdownCtx, cancel := context.WithTimeout(serverCtx, 10*time.Second)
		defer cancel()

		go func() {
			<-shutdownCtx.Done()
			if shutdownCtx.Err() == context.DeadlineExceeded {
				log.Fatal("Graceful shutdown timed out.. forcing exit.")
			}
		}()

		if err := server.Shutdown(shutdownCtx); err != nil {
			log.Fatal(err)
		}
		serverStopCtx()
	}()

	log.Printf("DevPlanet API Gateway listening on port %d...", cfg.Port)
	if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		log.Fatalf("Server listen error: %v\n", err)
	}

	<-serverCtx.Done()
	log.Println("Server shut down successfully.")
}
