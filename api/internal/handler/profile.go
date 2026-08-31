package handler

import (
	"encoding/json"
	"net/http"
	"strings"

	"github.com/spandev/devplanet/api/internal/github"
	"github.com/spandev/devplanet/api/internal/model"
)

// ProfileHandler handles requests for GitHub user profile and planet data.
type ProfileHandler struct {
	ghClient *github.Client
}

// NewProfileHandler creates a new ProfileHandler instance.
func NewProfileHandler(ghClient *github.Client) *ProfileHandler {
	return &ProfileHandler{
		ghClient: ghClient,
	}
}

// HandleGetProfile fetches GitHub data for the given username and returns the normalized profile.
func (h *ProfileHandler) HandleGetProfile(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		writeJSONError(w, http.StatusMethodNotAllowed, "method not allowed")
		return
	}

	// Extract username from URL path: /api/v1/profile/{username}
	pathParts := strings.Split(strings.Trim(r.URL.Path, "/"), "/")
	if len(pathParts) < 4 || pathParts[3] == "" {
		writeJSONError(w, http.StatusBadRequest, "username parameter is required")
		return
	}
	username := pathParts[3]

	rawUser, rateLimit, err := h.ghClient.FetchUserPlanetData(r.Context(), username)
	if err != nil {
		writeJSONError(w, http.StatusBadGateway, err.Error())
		return
	}

	normalized := model.NormalizeGitHubUser(rawUser)

	response := map[string]any{
		"profile":   normalized,
		"rateLimit": rateLimit,
	}

	writeJSON(w, http.StatusOK, response)
}

func writeJSON(w http.ResponseWriter, status int, data any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(data)
}

func writeJSONError(w http.ResponseWriter, status int, message string) {
	writeJSON(w, status, map[string]string{"error": message})
}
