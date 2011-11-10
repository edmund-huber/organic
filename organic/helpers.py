import ast
import _ast
import urllib

class BadURL(ValueError):
    pass

def make_rel_link(module, *args, **kwargs):
    path, qsl = validate_method_call(module, 'GET', args, kwargs)
    if qsl:
        return '/%s?%s' % (path, urllib.urlencode(qsl))
    else:
        return path

def validate_method_call(module, method, args, kwargs):
    path = get_path_of_module(module)
    req_args, opt_args = get_args_of_method(path, method)
    # Must have the right number of required args
    if len(args) == len(req_args):
        # No mystery arguments
        if set(kwargs.keys()) <= set(opt_args):
            # OK, make the query string list
            qsl = []
            for i, a in enumerate(req_args):
                qsl.append((a, args[i]))
            for a in opt_args:
                qsl.append((a, kwargs[a]))
            # And determine the path.
            path = '/'.join(module.__name__.split('.')[1:])
            return path or '/', qsl
    raise BadURL()
    
def get_path_of_module(module):
    path = module.__file__
    return path[:-1] if path[-1] == 'c' else path

def get_args_of_method(path, verb):
    all_args = None
    for e in ast.parse(open(path).read()).body:
        if isinstance(e, _ast.FunctionDef) and (e.name == verb):
            all_args = [arg.id for arg in e.args.args]
            default_count = len(e.args.defaults)
    if all_args is None:
        raise Exception('method not found! %s %s' % (path, verb))
    else:
        return all_args[:-default_count], all_args[-default_count:]
