package queue

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"time"

	"github.com/google/uuid"
	"github.com/redis/go-redis/v9"
)

const (
	defaultJobTTL    = 24 * time.Hour
	defaultQueueName = "queue:planet_tasks"
)

var (
	// ErrJobNotFound is returned when a job ID does not exist.
	ErrJobNotFound = errors.New("queue: job not found")
)

// TaskQueue manages job submission, retrieval, and dequeuing via Redis.
type TaskQueue struct {
	client    *redis.Client
	queueName string
}

// NewTaskQueue creates a new TaskQueue instance.
func NewTaskQueue(client *redis.Client, queueName string) *TaskQueue {
	if queueName == "" {
		queueName = defaultQueueName
	}
	return &TaskQueue{
		client:    client,
		queueName: queueName,
	}
}

func (q *TaskQueue) jobKey(jobID string) string {
	return fmt.Sprintf("job:%s", jobID)
}

// Enqueue creates a new job record and pushes it to the work queue.
func (q *TaskQueue) Enqueue(ctx context.Context, jobType, username string) (*Job, error) {
	if q.client == nil {
		return nil, errors.New("queue: redis client is not connected")
	}

	now := time.Now().UTC()
	job := &Job{
		ID:        uuid.New().String(),
		Type:      jobType,
		Username:  username,
		Status:    StatusPending,
		Progress:  0,
		Stage:     "queued",
		CreatedAt: now,
		UpdatedAt: now,
	}

	data, err := json.Marshal(job)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal job: %w", err)
	}

	pipe := q.client.TxPipeline()
	pipe.Set(ctx, q.jobKey(job.ID), data, defaultJobTTL)
	pipe.RPush(ctx, q.queueName, job.ID)

	if _, err := pipe.Exec(ctx); err != nil {
		return nil, fmt.Errorf("failed to enqueue job: %w", err)
	}

	return job, nil
}

// GetJob retrieves the current state and result of a job.
func (q *TaskQueue) GetJob(ctx context.Context, jobID string) (*Job, error) {
	if q.client == nil {
		return nil, errors.New("queue: redis client is not connected")
	}

	val, err := q.client.Get(ctx, q.jobKey(jobID)).Result()
	if err != nil {
		if errors.Is(err, redis.Nil) {
			return nil, ErrJobNotFound
		}
		return nil, fmt.Errorf("failed to get job: %w", err)
	}

	var job Job
	if err := json.Unmarshal([]byte(val), &job); err != nil {
		return nil, fmt.Errorf("failed to decode job: %w", err)
	}

	return &job, nil
}

// UpdateJob updates the status, progress, stage, error, or result of an existing job.
func (q *TaskQueue) UpdateJob(ctx context.Context, job *Job) error {
	if q.client == nil {
		return errors.New("queue: redis client is not connected")
	}

	job.UpdatedAt = time.Now().UTC()
	data, err := json.Marshal(job)
	if err != nil {
		return fmt.Errorf("failed to marshal job update: %w", err)
	}

	return q.client.Set(ctx, q.jobKey(job.ID), data, defaultJobTTL).Err()
}

// Dequeue pops the next job ID from the queue, blocking up to timeout.
func (q *TaskQueue) Dequeue(ctx context.Context, timeout time.Duration) (string, error) {
	if q.client == nil {
		return "", errors.New("queue: redis client is not connected")
	}

	res, err := q.client.BLPop(ctx, timeout, q.queueName).Result()
	if err != nil {
		if errors.Is(err, redis.Nil) {
			return "", nil // Timeout with no work
		}
		return "", fmt.Errorf("failed to dequeue job: %w", err)
	}

	if len(res) < 2 {
		return "", nil
	}

	return res[1], nil
}
