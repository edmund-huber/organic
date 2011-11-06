import re

def rage():
    return 'rawwwrrr!'

def router(verb, path, **kwargs):
    if verb == 'GET':
        if len(path) == 2 and re.search('^[Ff]+[Uu]*$', path[1]):
            return rage
    return None
