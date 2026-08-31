package unit_test

import (
	"testing"
	"time"

	"github.com/spandev/devplanet/api/internal/github"
	"github.com/spandev/devplanet/api/internal/model"
)

func TestNormalizeGitHubUser(t *testing.T) {
	raw := &github.UserNode{
		Login:        "octocat",
		Name:         "The Octocat",
		Bio:          "GitHub mascot",
		AvatarURL:    "https://avatars.githubusercontent.com/u/583231",
		CreatedAt:    time.Now().Add(-24 * 365 * time.Hour),
		Followers:    github.TotalCountNode{TotalCount: 100},
		Following:    github.TotalCountNode{TotalCount: 5},
		Repositories: github.TotalCountNode{TotalCount: 8},
		ContributionsCollection: github.ContributionsNode{
			TotalCommitContributions:            150,
			TotalIssueContributions:             10,
			TotalPullRequestContributions:       20,
			TotalPullRequestReviewContributions: 5,
			ContributionCalendar: github.ContributionCalendarNode{
				TotalContributions: 185,
				Weeks: []github.ContributionWeekNode{
					{
						ContributionDays: []github.ContributionDayNode{
							{Date: "2026-01-01", ContributionCount: 5, Color: "#216e39"},
						},
					},
				},
			},
		},
		PinnedItems: github.PinnedItemsConnection{
			Nodes: []github.RepositoryNode{
				{
					Name:           "Spoon-Knife",
					Description:    "This repo is for spoon-knife experiments.",
					StargazerCount: 1200,
					ForkCount:      500,
					PrimaryLanguage: &github.LanguageNode{
						Name:  "Go",
						Color: "#00ADD8",
					},
					Languages: github.LanguageConnection{
						TotalSize: 1000,
						Edges: []github.LanguageEdge{
							{
								Size: 1000,
								Node: github.LanguageNode{Name: "Go", Color: "#00ADD8"},
							},
						},
					},
				},
			},
		},
	}

	profile := model.NormalizeGitHubUser(raw)
	if profile == nil {
		t.Fatal("expected profile to not be nil")
	}

	if profile.Username != "octocat" {
		t.Errorf("expected username 'octocat', got '%s'", profile.Username)
	}

	if len(profile.Landforms) != 1 {
		t.Fatalf("expected 1 landform, got %d", len(profile.Landforms))
	}

	if !profile.Landforms[0].IsPinned {
		t.Errorf("expected Spoon-Knife repo to be marked as pinned")
	}

	if len(profile.LanguageSummary) != 1 || profile.LanguageSummary[0].Name != "Go" {
		t.Errorf("expected language summary to contain Go, got %+v", profile.LanguageSummary)
	}

	if profile.LanguageSummary[0].Percentage != 100.0 {
		t.Errorf("expected 100%% Go, got %f", profile.LanguageSummary[0].Percentage)
	}
}
