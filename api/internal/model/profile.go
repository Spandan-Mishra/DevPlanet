package model

import (
	"time"

	"github.com/spandev/devplanet/api/internal/github"
)

// LanguageStat summarizes aggregate language distribution across repositories.
type LanguageStat struct {
	Name       string  `json:"name"`
	Color      string  `json:"color"`
	Bytes      int     `json:"bytes"`
	Percentage float64 `json:"percentage"`
}

// LandformRepo represents a repository mapped to a planetary landform.
type LandformRepo struct {
	Name            string               `json:"name"`
	Description     string               `json:"description"`
	Stars           int                  `json:"stars"`
	Forks           int                  `json:"forks"`
	CommitCount     int                  `json:"commitCount"`
	PrimaryLanguage *github.LanguageNode `json:"primaryLanguage,omitempty"`
	Languages       []LanguageStat       `json:"languages"`
	IsPinned        bool                 `json:"isPinned"`
	CreatedAt       time.Time            `json:"createdAt"`
	PushedAt        time.Time            `json:"pushedAt"`
}

// UserPlanetProfile is the normalized payload prepared for The Forge engine.
type UserPlanetProfile struct {
	Username        string                       `json:"username"`
	Name            string                       `json:"name"`
	Bio             string                       `json:"bio"`
	AvatarURL       string                       `json:"avatarUrl"`
	AccountAgeDays  int                          `json:"accountAgeDays"`
	Followers       int                          `json:"followers"`
	Following       int                          `json:"following"`
	TotalRepos      int                          `json:"totalRepos"`
	TotalCommits    int                          `json:"totalCommits"`
	TotalPRs        int                          `json:"totalPRs"`
	TotalIssues     int                          `json:"totalIssues"`
	TotalReviews    int                          `json:"totalReviews"`
	LanguageSummary []LanguageStat               `json:"languageSummary"`
	Landforms       []LandformRepo               `json:"landforms"`
	ActivityHeatmap []github.ContributionDayNode `json:"activityHeatmap"`
}

// NormalizeGitHubUser transforms raw GitHub GraphQL nodes into our standardized domain model.
func NormalizeGitHubUser(raw *github.UserNode) *UserPlanetProfile {
	if raw == nil {
		return nil
	}

	days := int(time.Since(raw.CreatedAt).Hours() / 24)
	if days < 1 {
		days = 1
	}

	// 1. Flatten activity heatmap
	var heatmap []github.ContributionDayNode
	for _, week := range raw.ContributionsCollection.ContributionCalendar.Weeks {
		heatmap = append(heatmap, week.ContributionDays...)
	}

	// 2. Track unique repos (combining pinned and top repos)
	repoMap := make(map[string]LandformRepo)
	pinnedSet := make(map[string]bool)

	for _, node := range raw.PinnedItems.Nodes {
		pinnedSet[node.Name] = true
	}

	// Aggregate global language byte count
	globalLangBytes := make(map[string]int)
	globalLangColors := make(map[string]string)
	totalBytes := 0

	processRepo := func(node github.RepositoryNode, isPinned bool) {
		if _, exists := repoMap[node.Name]; exists {
			return
		}

		var repoLangs []LanguageStat
		for _, edge := range node.Languages.Edges {
			repoLangs = append(repoLangs, LanguageStat{
				Name:  edge.Node.Name,
				Color: edge.Node.Color,
				Bytes: edge.Size,
			})
			globalLangBytes[edge.Node.Name] += edge.Size
			globalLangColors[edge.Node.Name] = edge.Node.Color
			totalBytes += edge.Size
		}

		commits := 0
		if node.DefaultBranchRef != nil {
			commits = node.DefaultBranchRef.Target.History.TotalCount
		}

		repoMap[node.Name] = LandformRepo{
			Name:            node.Name,
			Description:     node.Description,
			Stars:           node.StargazerCount,
			Forks:           node.ForkCount,
			CommitCount:     commits,
			PrimaryLanguage: node.PrimaryLanguage,
			Languages:       repoLangs,
			IsPinned:        isPinned,
			CreatedAt:       node.CreatedAt,
			PushedAt:        node.PushedAt,
		}
	}

	for _, node := range raw.PinnedItems.Nodes {
		processRepo(node, true)
	}

	for _, node := range raw.TopRepositories.Nodes {
		processRepo(node, pinnedSet[node.Name])
	}

	var landforms []LandformRepo
	for _, repo := range repoMap {
		landforms = append(landforms, repo)
	}

	// 3. Compute normalized global language percentages
	var langSummary []LanguageStat
	for name, bytes := range globalLangBytes {
		var pct float64
		if totalBytes > 0 {
			pct = float64(bytes) / float64(totalBytes) * 100
		}
		langSummary = append(langSummary, LanguageStat{
			Name:       name,
			Color:      globalLangColors[name],
			Bytes:      bytes,
			Percentage: pct,
		})
	}

	return &UserPlanetProfile{
		Username:        raw.Login,
		Name:            raw.Name,
		Bio:             raw.Bio,
		AvatarURL:       raw.AvatarURL,
		AccountAgeDays:  days,
		Followers:       raw.Followers.TotalCount,
		Following:       raw.Following.TotalCount,
		TotalRepos:      raw.Repositories.TotalCount,
		TotalCommits:    raw.ContributionsCollection.TotalCommitContributions,
		TotalPRs:        raw.ContributionsCollection.TotalPullRequestContributions,
		TotalIssues:     raw.ContributionsCollection.TotalIssueContributions,
		TotalReviews:    raw.ContributionsCollection.TotalPullRequestReviewContributions,
		LanguageSummary: langSummary,
		Landforms:       landforms,
		ActivityHeatmap: heatmap,
	}
}
