package handler

import (
	"encoding/json"
	"net/http"
	"strings"
	"time"

	"github.com/spandev/devplanet/api/internal/cache"
	"github.com/spandev/devplanet/api/internal/github"
	"github.com/spandev/devplanet/api/internal/model"
	"github.com/spandev/devplanet/api/internal/queue"
)

// PlanetHandler handles planet data retrieval and async generation dispatch.
type PlanetHandler struct {
	cache     cache.Cacher
	taskQueue *queue.TaskQueue
	ghClient  *github.Client
}

// NewPlanetHandler creates a new PlanetHandler instance.
func NewPlanetHandler(c cache.Cacher, taskQueue *queue.TaskQueue, ghClient *github.Client) *PlanetHandler {
	return &PlanetHandler{
		cache:     c,
		taskQueue: taskQueue,
		ghClient:  ghClient,
	}
}

// HandlePlanet routes GET and POST requests for planet data and generation.
func (h *PlanetHandler) HandlePlanet(w http.ResponseWriter, r *http.Request) {
	// Expected paths:
	// GET  /api/v1/planet/{username}
	// POST /api/v1/planet/{username}/generate
	pathParts := strings.Split(strings.Trim(r.URL.Path, "/"), "/")
	if len(pathParts) < 4 || pathParts[3] == "" {
		writeJSONError(w, http.StatusBadRequest, "username parameter is required")
		return
	}

	username := pathParts[3]
	isGenerateAction := len(pathParts) >= 5 && pathParts[4] == "generate"

	if isGenerateAction {
		h.handleAsyncGenerate(w, r, username)
		return
	}

	switch r.Method {
	case http.MethodGet:
		h.handleGetPlanet(w, r, username)
	default:
		writeJSONError(w, http.StatusMethodNotAllowed, "method not allowed")
	}
}

// handleAsyncGenerate enqueues a background generation job or returns cached data if ready.
func (h *PlanetHandler) handleAsyncGenerate(w http.ResponseWriter, r *http.Request, username string) {
	if r.Method != http.MethodPost {
		writeJSONError(w, http.StatusMethodNotAllowed, "method not allowed")
		return
	}

	cacheKey := "planet:" + username
	var cachedProfile model.UserPlanetProfile
	if err := h.cache.Get(r.Context(), cacheKey, &cachedProfile); err == nil {
		writeJSON(w, http.StatusOK, map[string]any{
			"status": "completed",
			"stage":  "done",
			"cached": true,
			"result": cachedProfile,
		})
		return
	}

	job, err := h.taskQueue.Enqueue(r.Context(), "generate_planet", username)
	if err != nil {
		writeJSONError(w, http.StatusInternalServerError, "failed to enqueue generation task: "+err.Error())
		return
	}

	writeJSON(w, http.StatusAccepted, map[string]any{
		"jobId":    job.ID,
		"status":   job.Status,
		"stage":    job.Stage,
		"username": job.Username,
	})
}

// handleGetPlanet retrieves cached profile or performs a synchronous cache-aside fetch.
func (h *PlanetHandler) handleGetPlanet(w http.ResponseWriter, r *http.Request, username string) {
	cacheKey := "planet:" + username
	var cachedProfile model.UserPlanetProfile

	if err := h.cache.Get(r.Context(), cacheKey, &cachedProfile); err == nil {
		w.Header().Set("X-Cache", "HIT")
		writeJSON(w, http.StatusOK, map[string]any{
			"profile": cachedProfile,
			"source":  "cache",
		})
		return
	}

	// Cache miss: synchronous fallback
	rawUser, rateLimit, err := h.ghClient.FetchUserPlanetData(r.Context(), username)
	if err != nil {
		writeJSONError(w, http.StatusBadGateway, err.Error())
		return
	}

	normalized := model.NormalizeGitHubUser(rawUser)
	_ = h.cache.Set(r.Context(), cacheKey, normalized, 24*time.Hour)

	w.Header().Set("X-Cache", "MISS")
	writeJSON(w, http.StatusOK, map[string]any{
		"profile":   normalized,
		"rateLimit": rateLimit,
		"source":    "github",
	})
}

func writeJSON(w http.ResponseWriter, status int, data any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(data)
}

func writeJSONError(w http.ResponseWriter, status int, message string) {
	writeJSON(w, status, map[string]string{"error": message})
}
