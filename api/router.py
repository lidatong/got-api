from collections import defaultdict


class Router:
    def __init__(self, app):
        self.app = app
        self.routes = defaultdict(lambda: defaultdict(_routes_dict))

    def __getitem__(self, item):
        return self.routes[item]

    def route(self, path):
        def route_f(f):
            self.routes[f.__name__]['path'] = path
            return self.app.route(path)(f)

        return route_f


def _routes_dict():
    d = {}
    d.setdefault('sort', None)
    d.setdefault('search', False)
    return d
