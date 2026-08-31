package github

// UserProfileGraphQLQuery fetches all requisite profile, contribution, and repository data in a single round-trip.
const UserProfileGraphQLQuery = `
query GetUserPlanetData($username: String!) {
  rateLimit {
    limit
    cost
    remaining
    resetAt
  }
  user(login: $username) {
    login
    name
    bio
    avatarUrl
    createdAt
    followers {
      totalCount
    }
    following {
      totalCount
    }
    repositories(ownerAffiliations: OWNER, privacy: PUBLIC) {
      totalCount
    }
    contributionsCollection {
      totalCommitContributions
      totalIssueContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
            color
          }
        }
      }
    }
    pinnedItems(first: 6, types: [REPOSITORY]) {
      totalCount
      nodes {
        ... on Repository {
          name
          description
          isFork
          isArchived
          stargazerCount
          forkCount
          createdAt
          pushedAt
          primaryLanguage {
            name
            color
          }
          languages(first: 8, orderBy: {field: SIZE, direction: DESC}) {
            totalSize
            edges {
              size
              node {
                name
                color
              }
            }
          }
          defaultBranchRef {
            target {
              ... on Commit {
                history {
                  totalCount
                }
              }
            }
          }
        }
      }
    }
    topRepositories: repositories(
      first: 15
      ownerAffiliations: OWNER
      privacy: PUBLIC
      orderBy: {field: STARGAZERS, direction: DESC}
    ) {
      totalCount
      nodes {
        name
        description
        isFork
        isArchived
        stargazerCount
        forkCount
        createdAt
        pushedAt
        primaryLanguage {
          name
          color
        }
        languages(first: 8, orderBy: {field: SIZE, direction: DESC}) {
          totalSize
          edges {
            size
            node {
              name
              color
            }
          }
        }
        defaultBranchRef {
          target {
            ... on Commit {
              history {
                totalCount
              }
            }
          }
        }
      }
    }
  }
}
`
