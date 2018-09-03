import json
from collections import Counter, defaultdict
from functools import wraps
from itertools import product
from operator import attrgetter

import flask
from flask import Flask, request

from api.db import (select_episode_by_season_and_episode_ids,
                    select_episodes_by_season_id, select_ids_to_seasons)
from api.entities import __all__ as entities

app = Flask(__name__)


class AppEncoder(json.JSONEncoder):
    def default(self, o):
        for entity in entities:
            if isinstance(o, entity):
                return entity.schema().dump(o)
        try:
            iter(o)
        except TypeError:
            pass
        else:
            return list(o)
        return super().default(o)


app.json_encoder = AppEncoder


def routes_dict():
    d = {}
    d.setdefault('sort', None)
    d.setdefault('search', False)
    return d


routes = defaultdict(lambda: defaultdict(routes_dict))


def route(path):
    def route_f(f):
        routes[f.__name__]['path'] = path
        return app.route(path)(f)

    return route_f


def jsonify(f):
    routes[f.__name__]['content-type'] = 'application/json'

    @wraps(f)
    def jsonify_f(*args, **kwargs):
        return flask.jsonify(f(*args, **kwargs))

    return jsonify_f


def sortable(*fields):
    def sortable_f(f):
        routes[f.__name__]['params']['sort'] = fields

        @wraps(f)
        def f_with_sort(*args, **kwargs):
            sort_q = request.args.get('sort')
            if sort_q is None:
                return f(*args, **kwargs)
            sort = sort_q.split(',')
            return sorted(f(*args, **kwargs),
                          key=attrgetter(*sort))

        return f_with_sort

    return sortable_f


def search(*fields):
    def search_f(f):
        routes[f.__name__]['params']['search'] = True

        @wraps(f)
        def f_with_search(*args, **kwargs):
            q = request.args.get('q')
            results = f(*args, **kwargs)
            scored_results = Counter()
            if q is None:
                return results
            for field, result in product(fields, results):
                if q == str(getattr(result, field)):
                    scored_results[result] += 2
                try:
                    contains = q in getattr(result, field)
                except TypeError:
                    pass
                else:
                    if contains:
                        scored_results[result] += 1
            results = [result for result in results
                       if scored_results[result] > 0]
            return sorted(results, key=scored_results.get)

        return f_with_search

    return search_f


@route('/')
@jsonify
def index():
    return routes


@route('/seasons')
@jsonify
@sortable('id', 'synopsis')
@search('id')
def index_seasons():
    return list(select_ids_to_seasons().values())


@route('/seasons/<int:season_id>')
@jsonify
def show_season(season_id):
    season = select_ids_to_seasons()[season_id]
    return {"id": season.id, "synopsis": season.synopsis}


@route('/seasons/<int:season_id>/episodes')
@jsonify
@sortable('id')
def index_episodes(season_id):
    return sorted(select_episodes_by_season_id()[season_id],
                  key=attrgetter('id'))


@route('/seasons/<int:season_id>/episodes/<int:episode_id>')
@jsonify
def show_episode_in_season(season_id, episode_id):
    return select_episode_by_season_and_episode_ids()[season_id][episode_id]
