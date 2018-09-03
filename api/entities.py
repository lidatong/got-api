from dataclasses import dataclass
from typing import FrozenSet

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass(frozen=True)
class Episode:
    id: int
    title: str
    synopsis: str
    season_id: int


@dataclass_json
@dataclass(frozen=True)
class Season:
    id: int
    synopsis: str
    episodes: FrozenSet[Episode]


__all__ = [Episode, Season]
