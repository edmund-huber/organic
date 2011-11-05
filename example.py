import ast
import os.path
import sys
import urlparse

from helpers import unpack_method

def unzip2(xys):
    if xys:
        return zip(*xys)
    else:
        return [], []

class MultipleMatchingMethods(Exception):
    pass

class NoMatchingMethod(Exception):
    pass

class BrokenQuery(Exception):
    pass

def dispatch(environ, start_response):

    # Find the matching methods implemented through custom routers ..
    url_path_parts = filter(lambda p: '' != p, environ['PATH_INFO'].split('/'))
    methods = []
    for i, part in enumerate(url_path_parts):
        # Maybe import ..
        module_path = '.'.join(['app'] + url_path_parts[:i])
        try:
            __import__(module_path, globals(), locals(), [], -1)
            module = sys.modules[module_path]
            # if there's a module.router, then do what it asks
            if hasattr(module, 'router'):
                try:
                    # the search shouldn't be ruined if this fails
                    method = module.router('GET', url_path_parts)
                    if method is not None:
                        methods.append(method)
                except Exception, e:
                    print >> sys.stderr, '** router fail: %s.router(%s, %s)' % (module_path, 'GET', url_path_parts)
        except ImportError, e:
            pass
        
    # Add the default method if it can be found.
    try:
        default_module_path = '.'.join(['app'] + url_path_parts)
        __import__(default_module_path, globals(), locals(), [], -1)
        default_module = sys.modules[default_module_path]
        if hasattr(default_module, 'GET'):
            methods.append(getattr(default_module, 'GET'))
    except ImportError, e:
        pass

    # If more than one method matches, or no method matches, we
    # complain.
    if len(methods) > 1:
        raise MultipleMatchingMethods(environ['PATH_INFO'], methods)
    if len(methods) == 0:
        raise NoMatchingMethod(environ['PATH_INFO'])
    else:
        method = methods[0]

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
