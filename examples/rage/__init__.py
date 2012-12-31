import organic.response
import organic.status
import re

def router(verb, path, **kwargs):
    if verb == 'GET':
        if (len(path) == 1) and re.search('^[Ff]+[Uu]*$', path[0]):
            return organic.response.Raw(
                organic.status.OK,
                {'Content-Type': 'text/plain'},
                'rawwwrrr!')
    return False
