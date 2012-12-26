from mako.lookup import TemplateLookup
from mako.template import Template
import mimetypes
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

class BrokenHandler(Exception):
    pass

def dispatch(path, base_templates_path, environ, start_response):

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
                relevant_url_parts = url_path_parts[i:]
                try:
                    # the search shouldn't be ruined if this fails
                    method = module.router('GET', relevant_url_parts)
                    if method is not None:
                        methods.append(method)
                except Exception, e:
                    print >> sys.stderr, '** router fail: %s.router(%s, %s), "%s"' % (module_path, 'GET', relevant_url_parts, e)
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
                methods.append(getattr(default_module, 'GET'))
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
 
    # Call the module.method to generate the response
    kwargs = dict(map(lambda (k, v): (k, v[0] if len(v) == 1 else v), urlparse.parse_qs(environ['QUERY_STRING']).items()))
    resp = method(**kwargs)
    path, filename = os.path.split(module.__file__)
    filename = filename.split('.')[-2:-1][0]
    lookup = TemplateLookup(directories=[base_templates_path])
    if dict == type(resp):
        # If we get a dict back,we should find the corresponding
        # template and feed in the dict.
        if filename == '__init__':
            raise BrokenHandler()
        else:
            start_response('200 OK', [('Content-type', 'text/html')])
            return Template(filename="%s/%s.html" % (path, filename), lookup=lookup).render(**resp).encode('utf-8')
    elif (tuple == type(resp)) and (str == type(resp[0])) and (str == type(resp[1])):
        # A content-type and some text.
        start_response('200 OK', [('Content-type', resp[0])])
        return resp[1]
    elif (tuple == type(resp)) and (str == type(resp[0])) and (dict == type(resp[1])):
        # A template name and a dict.
        start_response('200 OK', [('Content-type', 'text/html')])
        return Template(filename="%s/%s.html" % (path, resp[0]), lookup=lookup).render(**resp[1]).encode('utf-8')
    else:
        raise BrokenHandler()

def static_router(root, verb, path):
    fn = "%s/%s" % (root, '/'.join(path))
    def static():
        return mimetypes.guess_type(fn)[0], open(fn).read()
    return static
