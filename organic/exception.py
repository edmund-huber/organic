class NoMatchingRoute(Exception): pass
class MultipleMatchingRoutes(Exception): pass

class RouteException(Exception):
    def __init__(self, status):
        self.status = status
