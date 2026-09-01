from datetime import datetime

from pydantic import AliasChoices, BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class ForgeBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class LanguageStat(ForgeBaseModel):
    name: str
    color: str
    bytes: int
    percentage: float


class PrimaryLanguage(ForgeBaseModel):
    name: str
    color: str


class LandformRepo(ForgeBaseModel):
    name: str
    description: str | None = None
    stars: int = 0
    forks: int = 0
    commit_count: int = 0
    primary_language: PrimaryLanguage | None = None
    languages: list[LanguageStat] = []
    is_pinned: bool = False
    created_at: datetime | None = None
    pushed_at: datetime | None = None


class ContributionDay(ForgeBaseModel):
    date: str
    contribution_count: int = 0
    color: str = "#ebedf0"


class UserPlanetProfileRequest(ForgeBaseModel):
    username: str
    name: str | None = None
    bio: str | None = None
    avatar_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices("avatarUrl", "avatar_url", "avatarURL"),
        serialization_alias="avatarUrl",
    )
    account_age_days: int = 1
    followers: int = 0
    following: int = 0
    total_repos: int = 0
    total_commits: int = 0
    total_prs: int = Field(
        default=0,
        validation_alias=AliasChoices("totalPRs", "total_prs", "totalPrs"),
        serialization_alias="totalPRs",
    )
    total_issues: int = 0
    total_reviews: int = 0
    language_summary: list[LanguageStat] = []
    landforms: list[LandformRepo] = []
    activity_heatmap: list[ContributionDay] = []
