from collections.__init__ import Counter
from functools import wraps
from itertools import product

import flask
from flask import request

from api.app import router


def jsonify(f):
    router[f.__name__]['content-type'] = 'application/json'

    @wraps(f)
    def jsonify_f(*args, **kwargs):
        return flask.jsonify(f(*args, **kwargs))

    return jsonify_f


def search(*fields):
    def search_f(f):
        router[f.__name__]['params']['search'] = True

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
