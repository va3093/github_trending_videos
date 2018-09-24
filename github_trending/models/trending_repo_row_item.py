from typing import NamedTuple


class TrendingRepoRowItem(NamedTuple):
    owner: str
    avatar: str
    repo: str
    stars: str
    description: str
    link: str