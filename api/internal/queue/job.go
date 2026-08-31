package queue

import (
	"time"
)

// JobStatus defines the state of an asynchronous generation job.
type JobStatus string

const (
	StatusPending    JobStatus = "pending"
	StatusProcessing JobStatus = "processing"
	StatusCompleted  JobStatus = "completed"
	StatusFailed     JobStatus = "failed"
)

// Job represents a background task for planet generation.
type Job struct {
	ID        string    `json:"id"`
	Type      string    `json:"type"`
	Username  string    `json:"username"`
	Status    JobStatus `json:"status"`
	Progress  int       `json:"progress"` // 0 - 100
	Stage     string    `json:"stage"`    // e.g. "fetching_github", "running_forge", "persisting"
	Result    any       `json:"result,omitempty"`
	Error     string    `json:"error,omitempty"`
	CreatedAt time.Time `json:"createdAt"`
	UpdatedAt time.Time `json:"updatedAt"`
}
