import collections
import functools
import mako.lookup
import mimetypes
import os.path
import sys

import organic.exception


HandlerInfo = collections.namedtuple('HandlerInfo', ['type', 'import_path'])


def choose(web_path, base_templates_path, method, url_path):

    # Where to look for templates.
    lookup = mako.lookup.TemplateLookup(directories=[base_templates_path])

    # Custom routers: /b/a -> ${web_path}.router OR 
    #                         ${web_path}.b.router OR
    #                         ${web_path}.b.a.router
    handlers = []
    handler_infos = []
    for i in range(len(url_path) + 1):
        module_path = '.'.join(web_path + url_path[:i])
        # TODO: should add some checking to be sure this is a module
        # we feel safe importing.
        try:
            __import__(module_path, globals(), locals(), [], -1)
            module = sys.modules[module_path]
            if hasattr(module, 'router'):
                # We only use the deepest custom router.
                if handlers:
                    handlers.pop()
                    handler_infos.pop()
                handlers.append(functools.partial(run_and_interpret, lookup, module, functools.partial(module.router, method, url_path[i:])))
                handler_infos.append(HandlerInfo('custom', '%s.%s' % (module_path, 'router')))
        except ImportError, e:
            pass

    # Default method: /b/a -> ${web_path}.b.a.${http_method}
    default_module_path = '.'.join(web_path + url_path)
    try:
        __import__(default_module_path, globals(), locals(), [], -1)
        if hasattr(module, method):
            # If there's a default method we don't use any custom router.
            handlers = [functools.partial(run_and_interpret, lookup, module, getattr(sys.modules[default_module_path], method))]
            handler_infos = [HandlerInfo('default', default_module_path)]
    except ImportError, e:
        pass

    # TODO: if nothing has worked so far, and there is a template in
    # the right place, just instantiate it with {}.

    # If more than one method matches, or no method matches, we
    # complain. This is here so that I can keep track of all the logic
    # of which handler to use. I want to be sure I am manipulating
    # this implicit (now explicit) list correctly and not just
    # clobbering things thoughtlessly.
    if len(handlers) > 1:
        raise organic.exception.MultipleMatchingRoutes('/'.join(url_path), handler_infos)
    if len(handlers) == 0:
        raise organic.exception.NoMatchingRoute('/'.join(web_path + url_path))
    else:
        return handlers[0]


def run_and_interpret(lookup, module, handler, **params):
    v = handler(**params)
    module_path = os.path.dirname(module.__file__)    

    if isinstance(v, dict):
        fn = os.path.join(module_path, module.__name__.split('.')[-1] + '.html')
        body = mako.template.Template(filename=fn, lookup=lookup).render(**v).encode('utf-8')
        return organic.status.OK, {'Content-Type': mimetypes.guess_type(fn)[0]}, body
        
    elif isinstance(v, organic.response.TemplateT):
        fn = os.path.join(module_path, v.path)
        if os.path.isfile(fn):
            if 'Content-Type' not in v.headers:
                v.headers['Content-Type'] = mimetypes.guess_type(fn)[0]
            body = mako.template.Template(filename=fn, lookup=lookup).render(**v.data).encode('utf-8')
            return v.status, v.headers, body
        else:
            raise organic.exception.RouteException(organic.status.SERVER_ERROR)

    elif isinstance(v, organic.response.Raw):
        if 'Content-Type' not in v.headers:
            raise organic.exception.RouteException(organic.status.SERVER_ERROR)
        else:
            return v.status, v.headers, v.body

    elif v is False:
        raise organic.exception.RouteException(organic.status.NOT_FOUND)

    else:
        raise organic.exception.RouteException(organic.status.SERVER_ERROR)
