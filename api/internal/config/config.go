package config

import (
	"os"
	"strconv"
)

// Config holds all service configuration loaded from environment variables.
type Config struct {
	Port         int
	GitHubToken  string
	ForgeURL     string
	RedisURL     string
	DatabaseURL  string
}

// Load reads configuration from environment variables with sensible defaults.
func Load() *Config {
	return &Config{
		Port:        getEnvAsInt("PORT", 8080),
		GitHubToken: os.Getenv("GITHUB_TOKEN"),
		ForgeURL:    getEnv("FORGE_URL", "http://localhost:8000"),
		RedisURL:    getEnv("REDIS_URL", "redis://localhost:6379"),
		DatabaseURL: getEnv("DATABASE_URL", "postgres://postgres:postgres@localhost:5432/devplanet?sslmode=disable"),
	}
}

func getEnv(key, fallback string) string {
	if val := os.Getenv(key); val != "" {
		return val
	}
	return fallback
}

func getEnvAsInt(key string, fallback int) int {
	if val := os.Getenv(key); val != "" {
		if intVal, err := strconv.Atoi(val); err == nil {
			return intVal
		}
	}
	return fallback
}
