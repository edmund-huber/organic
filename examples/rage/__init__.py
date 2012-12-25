import re

def rage():
    return 'rawwwrrr!'

def router(verb, path, **kwargs):
    if verb == 'GET':
        if (len(path) == 1) and re.search('^[Ff]+[Uu]*$', path[0]):
            return rage
    return None
