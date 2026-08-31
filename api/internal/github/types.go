package github

import "time"

// RateLimitInfo tracks remaining GitHub API quota.
type RateLimitInfo struct {
	Limit     int       `json:"limit"`
	Cost      int       `json:"cost"`
	Remaining int       `json:"remaining"`
	ResetAt   time.Time `json:"resetAt"`
}

// GraphQLError represents an error returned in a GraphQL response.
type GraphQLError struct {
	Message   string   `json:"message"`
	Type      string   `json:"type,omitempty"`
	Path      []any    `json:"path,omitempty"`
	Locations []struct {
		Line   int `json:"line"`
		Column int `json:"column"`
	} `json:"locations,omitempty"`
}

// GraphQLResponse is the top-level wrapper for all GitHub GraphQL responses.
type GraphQLResponse struct {
	Data   *GraphQLData   `json:"data"`
	Errors []GraphQLError `json:"errors,omitempty"`
}

// GraphQLData wraps the root user query and rate limit status.
type GraphQLData struct {
	RateLimit *RateLimitInfo `json:"rateLimit"`
	User      *UserNode      `json:"user"`
}

// UserNode represents the raw GitHub user profile data.
type UserNode struct {
	Login                  string                 `json:"login"`
	Name                   string                 `json:"name"`
	Bio                    string                 `json:"bio"`
	AvatarURL              string                 `json:"avatarUrl"`
	CreatedAt              time.Time              `json:"createdAt"`
	Followers              TotalCountNode         `json:"followers"`
	Following              TotalCountNode         `json:"following"`
	Repositories           TotalCountNode         `json:"repositories"`
	ContributionsCollection ContributionsNode      `json:"contributionsCollection"`
	PinnedItems            PinnedItemsConnection  `json:"pinnedItems"`
	TopRepositories        RepositoryConnection   `json:"topRepositories"`
}

// TotalCountNode is a generic helper for nodes containing only totalCount.
type TotalCountNode struct {
	TotalCount int `json:"totalCount"`
}

// ContributionsNode contains breakdown of user contributions over the past year.
type ContributionsNode struct {
	TotalCommitContributions            int                      `json:"totalCommitContributions"`
	TotalIssueContributions             int                      `json:"totalIssueContributions"`
	TotalPullRequestContributions       int                      `json:"totalPullRequestContributions"`
	TotalPullRequestReviewContributions int                      `json:"totalPullRequestReviewContributions"`
	RestrictedContributionsCount        int                      `json:"restrictedContributionsCount"`
	ContributionCalendar                ContributionCalendarNode `json:"contributionCalendar"`
}

// ContributionCalendarNode represents the 52-week activity calendar.
type ContributionCalendarNode struct {
	TotalContributions int                    `json:"totalContributions"`
	Weeks              []ContributionWeekNode `json:"weeks"`
}

// ContributionWeekNode represents a single week of activity.
type ContributionWeekNode struct {
	ContributionDays []ContributionDayNode `json:"contributionDays"`
}

// ContributionDayNode represents an individual day's contributions.
type ContributionDayNode struct {
	Date              string `json:"date"`
	ContributionCount int    `json:"contributionCount"`
	Color             string `json:"color"`
}

// RepositoryConnection holds a list of repositories.
type RepositoryConnection struct {
	TotalCount int              `json:"totalCount"`
	Nodes      []RepositoryNode `json:"nodes"`
}

// PinnedItemsConnection holds pinned repositories.
type PinnedItemsConnection struct {
	TotalCount int              `json:"totalCount"`
	Nodes      []RepositoryNode `json:"nodes"`
}

// RepositoryNode represents a GitHub repository with its languages and statistics.
type RepositoryNode struct {
	Name            string             `json:"name"`
	Description     string             `json:"description"`
	IsFork          bool               `json:"isFork"`
	IsArchived      bool               `json:"isArchived"`
	StargazerCount  int                `json:"stargazerCount"`
	ForkCount       int                `json:"forkCount"`
	CreatedAt       time.Time          `json:"createdAt"`
	PushedAt        time.Time          `json:"pushedAt"`
	PrimaryLanguage *LanguageNode      `json:"primaryLanguage"`
	Languages       LanguageConnection `json:"languages"`
	DefaultBranchRef *BranchRefNode    `json:"defaultBranchRef"`
}

// BranchRefNode extracts commit history count.
type BranchRefNode struct {
	Target struct {
		History TotalCountNode `json:"history"`
	} `json:"target"`
}

// LanguageConnection holds language breakdown by bytes.
type LanguageConnection struct {
	TotalSize int            `json:"totalSize"`
	Edges     []LanguageEdge `json:"edges"`
}

// LanguageEdge maps language node to byte size.
type LanguageEdge struct {
	Size int          `json:"size"`
	Node LanguageNode `json:"node"`
}

// LanguageNode contains language name and color hex.
type LanguageNode struct {
	Name  string `json:"name"`
	Color string `json:"color"`
}
