class NoMatchingRoute(Exception):

    def __init__(self, path):
        self._path = path

    def __repr__(self):
        return 'No matching route for path="%s"' %  self._path


class MultipleMatchingRoutes(Exception):

    def __init__(self, path, routes):
        self._path = path
        self._routes = routes

    def __repr__(self):
        return 'Multiple matching route for path="%s":\n%s' % (self._path, '\n'.join(map(repr, self._routes)))


class RouteException(Exception):

    def __init__(self, status):
        self._status = status

    def __repr__(self):
        return 'Routing layer generated an error, "%s"' % self._status
