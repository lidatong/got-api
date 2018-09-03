import csv
from collections import defaultdict
from functools import lru_cache

from api.entities import Episode, Season


def read_csv(path, dtypes=None):
    def cast(row):
        return [dtype(col) for dtype, col in zip(dtypes, row)]

    with open(path) as fp:
        next(fp)
        reader = csv.reader(fp)
        reader = reader if dtypes is None else map(cast, reader)
        yield from reader


@lru_cache()
def select_episodes():
    table = read_csv('data/episodes.csv', dtypes=(int, int, str, str))
    return [Episode(e_id, title, synopsis, s_id)
            for s_id, e_id, title, synopsis in table]


@lru_cache()
def select_ids_to_seasons():
    table = read_csv('data/seasons.csv', dtypes=(int, str))
    return {id_: Season(id_,
                        synopsis,
                        frozenset(select_episodes_by_season_id()[id_]))
            for id_, synopsis in table}


@lru_cache()
def select_episodes_by_season_id():
    episodes = select_episodes()
    episodes_by_season_id = defaultdict(list)
    for episode in episodes:
        episodes_by_season_id[episode.season_id].append(episode)
    return episodes_by_season_id


@lru_cache()
def select_episode_by_season_and_episode_ids():
    episodes_by_season_id = select_episodes_by_season_id()
    episodes_by_season_and_episode_id = defaultdict(dict)
    for season_id, episodes in episodes_by_season_id.items():
        for episode in episodes:
            episodes_by_season_id[season_id][episode.id] = episode
    return episodes_by_season_and_episode_id
