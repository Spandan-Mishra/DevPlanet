package cache

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"time"

	"github.com/redis/go-redis/v9"
)

var (
	// ErrCacheMiss is returned when the requested key does not exist in cache.
	ErrCacheMiss = errors.New("cache: key not found")
)

// Cacher defines the caching interface for planet and profile data.
type Cacher interface {
	Get(ctx context.Context, key string, dest any) error
	Set(ctx context.Context, key string, value any, ttl time.Duration) error
	Delete(ctx context.Context, key string) error
}

// RedisCache implements Cacher using Redis.
type RedisCache struct {
	client *redis.Client
	prefix string
}

// NewRedisCache creates a new RedisCache with a key namespace prefix.
func NewRedisCache(client *redis.Client, prefix string) *RedisCache {
	return &RedisCache{
		client: client,
		prefix: prefix,
	}
}

func (c *RedisCache) formatKey(key string) string {
	if c.prefix == "" {
		return key
	}
	return fmt.Sprintf("%s:%s", c.prefix, key)
}

// Get retrieves and JSON-unmarshals a cached value by key.
func (c *RedisCache) Get(ctx context.Context, key string, dest any) error {
	if c.client == nil {
		return ErrCacheMiss
	}

	val, err := c.client.Get(ctx, c.formatKey(key)).Result()
	if err != nil {
		if errors.Is(err, redis.Nil) {
			return ErrCacheMiss
		}
		return fmt.Errorf("failed to get from cache: %w", err)
	}

	if err := json.Unmarshal([]byte(val), dest); err != nil {
		return fmt.Errorf("failed to unmarshal cached value: %w", err)
	}

	return nil
}

// Set JSON-marshals and stores a value in Redis with a TTL.
func (c *RedisCache) Set(ctx context.Context, key string, value any, ttl time.Duration) error {
	if c.client == nil {
		return nil
	}

	data, err := json.Marshal(value)
	if err != nil {
		return fmt.Errorf("failed to marshal cache value: %w", err)
	}

	if err := c.client.Set(ctx, c.formatKey(key), data, ttl).Err(); err != nil {
		return fmt.Errorf("failed to set cache key: %w", err)
	}

	return nil
}

// Delete removes a key from Redis.
func (c *RedisCache) Delete(ctx context.Context, key string) error {
	if c.client == nil {
		return nil
	}

	return c.client.Del(ctx, c.formatKey(key)).Err()
}
