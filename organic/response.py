import collections

import organic.status

TemplateT = collections.namedtuple('Template', ['status', 'headers', 'path', 'data'])
def Template(path, data, status=organic.status.OK, headers={}):
    return TemplateT(status, headers, path, data)

Raw = collections.namedtuple('Raw', ['status', 'headers', 'body'])
