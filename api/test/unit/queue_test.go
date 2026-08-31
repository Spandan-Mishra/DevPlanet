package unit_test

import (
	"context"
	"testing"
	"time"

	"github.com/spandev/devplanet/api/internal/cache"
	"github.com/spandev/devplanet/api/internal/queue"
)

func TestCacheNilClientSafety(t *testing.T) {
	c := cache.NewRedisCache(nil, "test")
	ctx := context.Background()

	var dest string
	if err := c.Get(ctx, "nonexistent", &dest); err != cache.ErrCacheMiss {
		t.Errorf("expected ErrCacheMiss on nil redis client, got %v", err)
	}

	if err := c.Set(ctx, "key", "val", 1*time.Minute); err != nil {
		t.Errorf("expected nil error on Set with nil redis client, got %v", err)
	}

	if err := c.Delete(ctx, "key"); err != nil {
		t.Errorf("expected nil error on Delete with nil redis client, got %v", err)
	}
}

func TestQueueNilClientSafety(t *testing.T) {
	q := queue.NewTaskQueue(nil, "test_queue")
	ctx := context.Background()

	_, err := q.Enqueue(ctx, "generate", "octocat")
	if err == nil {
		t.Error("expected error when enqueuing with nil client")
	}

	_, err = q.GetJob(ctx, "some-id")
	if err == nil {
		t.Error("expected error when getting job with nil client")
	}

	_, err = q.Dequeue(ctx, 100*time.Millisecond)
	if err == nil {
		t.Error("expected error when dequeuing with nil client")
	}
}
