from functools import wraps
from operator import attrgetter

from flask import request

from api.app import router


def sortable(*fields):
    def sortable_f(f):
        router[f.__name__]['params']['sort'] = fields

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
