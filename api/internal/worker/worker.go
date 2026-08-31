package worker

import (
	"context"
	"log"
	"time"

	"github.com/spandev/devplanet/api/internal/cache"
	"github.com/spandev/devplanet/api/internal/github"
	"github.com/spandev/devplanet/api/internal/model"
	"github.com/spandev/devplanet/api/internal/queue"
)

// PlanetWorker consumes background planet generation tasks.
type PlanetWorker struct {
	taskQueue *queue.TaskQueue
	cache     cache.Cacher
	ghClient  *github.Client
}

// NewPlanetWorker creates a new PlanetWorker instance.
func NewPlanetWorker(taskQueue *queue.TaskQueue, c cache.Cacher, ghClient *github.Client) *PlanetWorker {
	return &PlanetWorker{
		taskQueue: taskQueue,
		cache:     c,
		ghClient:  ghClient,
	}
}

// Start runs the worker loop until the context is cancelled.
func (w *PlanetWorker) Start(ctx context.Context) {
	log.Println("PlanetWorker background loop started...")

	for {
		select {
		case <-ctx.Done():
			log.Println("PlanetWorker stopping...")
			return
		default:
			jobID, err := w.taskQueue.Dequeue(ctx, 2*time.Second)
			if err != nil {
				if ctx.Err() != nil {
					return
				}
				log.Printf("Worker dequeue error: %v\n", err)
				time.Sleep(1 * time.Second)
				continue
			}

			if jobID == "" {
				// BLPop timed out with no items in queue
				continue
			}

			w.processJob(ctx, jobID)
		}
	}
}

func (w *PlanetWorker) processJob(ctx context.Context, jobID string) {
	job, err := w.taskQueue.GetJob(ctx, jobID)
	if err != nil {
		log.Printf("Worker failed to get job %s: %v\n", jobID, err)
		return
	}

	log.Printf("Processing job %s for user '%s'...\n", job.ID, job.Username)

	// Stage 1: Ingest from GitHub
	job.Status = queue.StatusProcessing
	job.Stage = "fetching_github"
	job.Progress = 20
	_ = w.taskQueue.UpdateJob(ctx, job)

	rawUser, _, err := w.ghClient.FetchUserPlanetData(ctx, job.Username)
	if err != nil {
		job.Status = queue.StatusFailed
		job.Stage = "failed"
		job.Error = err.Error()
		_ = w.taskQueue.UpdateJob(ctx, job)
		log.Printf("Job %s failed at github fetch: %v\n", job.ID, err)
		return
	}

	// Stage 2: Normalization
	job.Stage = "normalizing_data"
	job.Progress = 50
	_ = w.taskQueue.UpdateJob(ctx, job)

	profile := model.NormalizeGitHubUser(rawUser)

	// Stage 3: Cache the normalized data (TTL: 24h)
	job.Stage = "caching_genome"
	job.Progress = 80
	_ = w.taskQueue.UpdateJob(ctx, job)

	cacheKey := "planet:" + job.Username
	_ = w.cache.Set(ctx, cacheKey, profile, 24*time.Hour)

	// Stage 4: Mark Complete
	job.Status = queue.StatusCompleted
	job.Stage = "done"
	job.Progress = 100
	job.Result = profile
	_ = w.taskQueue.UpdateJob(ctx, job)

	log.Printf("Job %s for user '%s' completed successfully.\n", job.ID, job.Username)
}
