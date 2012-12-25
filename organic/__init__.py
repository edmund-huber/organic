import os.path
import sys
import urlparse

import helpers

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

class CannotParse(Exception):
    pass

def dispatch(path, environ, start_response):

    # Find the matching methods implemented through custom routers ..
    url_path_parts = filter(lambda p: '' != p, environ['PATH_INFO'].split('/'))
    methods = []
    for i in range(len(url_path_parts) + 1):
        # Maybe import ..
        module_path = '.'.join([path] + url_path_parts[:i])
        try:
            __import__(module_path, globals(), locals(), [], -1)
            module = sys.modules[module_path]
            # if there's a module.router, then do what it asks
            if hasattr(module, 'router'):
                try:
                    # the search shouldn't be ruined if this fails
                    method = module.router('GET', url_path_parts)
                    if method is not None:
                        path = helpers.get_path_of_module(module)#__import__(method.__module__, globals(), locals(), [], -1))
                        required_args, optional_args = helpers.get_args_of_method(path, method.__name__)
                        methods.append((method, required_args, optional_args))
                except Exception, e:
                    print >> sys.stderr, '** router fail: %s.router(%s, %s), "%s"' % (module_path, 'GET', url_path_parts, e)
        except ImportError, e:
            pass        

    # Add the default method if it can be found.
    try:
        default_module_path = '.'.join([path] + url_path_parts)
        __import__(default_module_path, globals(), locals(), [], -1)
        default_module = sys.modules[default_module_path]
        if hasattr(default_module, 'GET'):
            # OK, also parse the file so that we figure out the
            # arguments and optional arguments.
            try:
                path = helpers.get_path_of_module(default_module)
                required_args, optional_args = helpers.get_args_of_method(path, 'GET')
                # Assumption: all arguments-with-defaults must come
                # after any regular argument.
                methods.append((getattr(default_module, 'GET'), required_args, optional_args))
            except Exception, e:
                raise CannotParse(e)
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
    method, required_args, optional_args = method
    url_query_kvs = urlparse.parse_qsl(environ['QUERY_STRING'])
    url_query_ks, _ = unzip2(url_query_kvs)

    # .. does it address all mandatory arguments?
    if set(required_args) > set(url_query_ks):
        raise BrokenQuery((environ['PATH_INFO'], environ['QUERY_STRING']))

    # .. does it have any keys that we don't even recognize?
    all_args = set(required_args) | set(optional_args)
    if set(url_query_ks) - all_args:
        raise BrokenQuery((environ['PATH_INFO'], environ['QUERY_STRING']))

    # OK collect the kwargs dict that we'll shove into the method.
    to_satisfy = all_args
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
