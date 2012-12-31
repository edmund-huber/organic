import functools
import mako.lookup
import sys

import organic.handlers

class NoMatchingMethod(Exception): pass
class MultipleMatchingMethods(Exception): pass

def choose(web_path, base_templates_path, url_path):

    # Where to look for templates.
    lookup = mako.lookup.TemplateLookup(directories=[base_templates_path])

    # Custom routers: /b/a -> ${web_path}.router OR 
    #                         ${web_path}.b.router OR
    #                         ${web_path}.b.a.router
    methods = []
    for i in range(len(url_path) + 1):
        module_path = '.'.join(web_path + url_path[:i])
        # TODO: should add some checking to be sure this is a module
        # we feel safe importing.
        try:
            __import__(module_path, globals(), locals(), [], -1)
            module = sys.modules[module_path]
            if hasattr(module, 'router'):
                relevant_url_path = url_path[i:]
                methods.append(functools.partial(organic.handlers.custom, lookup, module, relevant_url_path))
        except ImportError, e:
            pass

    # Default method: /b/a -> ${web_path}.b.a.${http_method}
    default_module_path = '.'.join(web_path + url_path)
    try:
        __import__(default_module_path, globals(), locals(), [], -1)
        methods.append(functools.partial(organic.handlers.default, lookup, sys.modules[default_module_path]))
    except ImportError, e:
        pass

    # TODO: if nothing has worked so far, and there is a template in
    # the right place, just instantiate it with {}.

    # If more than one method matches, or no method matches, we
    # complain.
    if len(methods) > 1:
        raise MultipleMatchingMethods('/'.join(url_path), methods)
    if len(methods) == 0:
        raise NoMatchingMethod('/'.join(web_path + url_path))
    else:
        return methods[0]
