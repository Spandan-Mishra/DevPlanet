package github

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

const (
	githubGraphQLEndpoint = "https://api.github.com/graphql"
	defaultTimeout        = 10 * time.Second
)

// Client handles communication with the GitHub GraphQL API.
type Client struct {
	token      string
	httpClient *http.Client
}

// NewClient creates a new GitHub GraphQL API client.
func NewClient(token string) *Client {
	return &Client{
		token: token,
		httpClient: &http.Client{
			Timeout: defaultTimeout,
		},
	}
}

type graphQLRequestBody struct {
	Query     string         `json:"query"`
	Variables map[string]any `json:"variables"`
}

// FetchUserPlanetData executes the single comprehensive GraphQL query for a GitHub username.
func (c *Client) FetchUserPlanetData(ctx context.Context, username string) (*UserNode, *RateLimitInfo, error) {
	if username == "" {
		return nil, nil, fmt.Errorf("username cannot be empty")
	}

	reqPayload := graphQLRequestBody{
		Query: UserProfileGraphQLQuery,
		Variables: map[string]any{
			"username": username,
		},
	}

	jsonBytes, err := json.Marshal(reqPayload)
	if err != nil {
		return nil, nil, fmt.Errorf("failed to marshal graphql payload: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, githubGraphQLEndpoint, bytes.NewBuffer(jsonBytes))
	if err != nil {
		return nil, nil, fmt.Errorf("failed to create http request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("User-Agent", "DevPlanet-Ingestion-Service/1.0")
	if c.token != "" {
		req.Header.Set("Authorization", fmt.Sprintf("Bearer %s", c.token))
	}

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, nil, fmt.Errorf("github api request failed: %w", err)
	}
	defer resp.Body.Close()

	bodyBytes, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, nil, fmt.Errorf("failed to read response body: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		return nil, nil, fmt.Errorf("github api returned status %d: %s", resp.StatusCode, string(bodyBytes))
	}

	var gqlResp GraphQLResponse
	if err := json.Unmarshal(bodyBytes, &gqlResp); err != nil {
		return nil, nil, fmt.Errorf("failed to decode graphql response: %w", err)
	}

	if len(gqlResp.Errors) > 0 {
		return nil, nil, fmt.Errorf("graphql error: %s", gqlResp.Errors[0].Message)
	}

	if gqlResp.Data == nil || gqlResp.Data.User == nil {
		return nil, nil, fmt.Errorf("user '%s' not found on github", username)
	}

	return gqlResp.Data.User, gqlResp.Data.RateLimit, nil
}
