package handler

import (
	"errors"
	"net/http"
	"strings"

	"github.com/spandev/devplanet/api/internal/queue"
)

// JobHandler handles job status and result polling endpoints.
type JobHandler struct {
	taskQueue *queue.TaskQueue
}

// NewJobHandler creates a new JobHandler instance.
func NewJobHandler(taskQueue *queue.TaskQueue) *JobHandler {
	return &JobHandler{taskQueue: taskQueue}
}

// HandleGetJob returns the status and progress of a background job.
func (h *JobHandler) HandleGetJob(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		writeJSONError(w, http.StatusMethodNotAllowed, "method not allowed")
		return
	}

	// Extract job ID from URL path: /api/v1/jobs/{jobId}
	pathParts := strings.Split(strings.Trim(r.URL.Path, "/"), "/")
	if len(pathParts) < 4 || pathParts[3] == "" {
		writeJSONError(w, http.StatusBadRequest, "job ID parameter is required")
		return
	}
	jobID := pathParts[3]

	job, err := h.taskQueue.GetJob(r.Context(), jobID)
	if err != nil {
		if errors.Is(err, queue.ErrJobNotFound) {
			writeJSONError(w, http.StatusNotFound, "job not found")
			return
		}
		writeJSONError(w, http.StatusInternalServerError, err.Error())
		return
	}

	writeJSON(w, http.StatusOK, job)
}
