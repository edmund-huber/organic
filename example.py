import ast
import os.path
import urlparse

from helpers import unpack_method

def unzip2(xys):
    if xys:
        return zip(*xys)
    else:
        return [], []

class BrokenQuery(Exception):
    pass

def dispatch(environ, start_response):

    # Find the appropriate module.method
    url_path_parts = filter(lambda p: '' != p, environ['PATH_INFO'].split('/'))
    if url_path_parts:
        module_path = '.'.join(['app'] + url_path_parts)
    else:
        module_path = 'app'

    # Maybe import
    if module_path not in globals():
        try:
            module = __import__(module_path, globals(), locals(), [], -1)
        except ImportError, e:
            print e
            raise NotImplementedError(environ['PATH_INFO'])
        method = reduce(lambda submo, p: getattr(submo, p), url_path_parts, module).GET

    # Check that the query is properly formatted:
    optional_args, method = unpack_method(method)
    url_query_kvs = urlparse.parse_qsl(environ['QUERY_STRING'])
    url_query_ks, _ = unzip2(url_query_kvs)
    # .. does it address all mandatory arguments?
    if set(method.func_code.co_varnames) - set(optional_args) > set(url_query_ks):
        raise BrokenQuery((environ['PATH_INFO'], environ['QUERY_STRING']))

    # OK collect the kwargs dict that we'll shove into the method.
    to_satisfy = set(method.func_code.co_varnames)
    kwargs = {}
    for k, v in url_query_kvs:
        if k in kwargs:
            raise BrokenQuery((environ['PATH_INFO'], environ['QUERY_STRING']))
        elif k in to_satisfy:
            kwargs[k] = v
            to_satisfy.remove(k)
 
    # Call the module.method to generate the response
    start_response('200 OK', [('Content-type', 'text/html')])
    return method(**kwargs)
