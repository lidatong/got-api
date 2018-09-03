from operator import attrgetter

from flask import Flask

from api.db import (select_episode_by_season_and_episode_ids,
                    select_episodes_by_season_id,
                    select_ids_to_seasons)
from api.decorators import jsonify, search, sortable
from api.encoder import AppEncoder
from api.router import Router

app = Flask(__name__)
app.json_encoder = AppEncoder
router = Router(app)


@router.route('/')
@jsonify
def index():
    return router


@router.route('/seasons')
@jsonify
@sortable('id', 'synopsis')
@search('id')
def index_seasons():
    return list(select_ids_to_seasons().values())


@router.route('/seasons/<int:season_id>')
@jsonify
def show_season(season_id):
    season = select_ids_to_seasons()[season_id]
    return {"id": season.id, "synopsis": season.synopsis}


@router.route('/seasons/<int:season_id>/episodes')
@jsonify
@sortable('id')
def index_episodes(season_id):
    return sorted(select_episodes_by_season_id()[season_id],
                  key=attrgetter('id'))


@router.route('/seasons/<int:season_id>/episodes/<int:episode_id>')
@jsonify
def show_episode_in_season(season_id, episode_id):
    return select_episode_by_season_and_episode_ids()[season_id][episode_id]
