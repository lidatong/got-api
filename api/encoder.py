import json

from api.entities import __all__ as entities


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
