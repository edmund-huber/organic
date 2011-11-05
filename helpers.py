import urllib

class BadURL(ValueError):
    pass

def optional_args(*args):
    def wrapper(f):
        return (args, f)
    return wrapper

def unpack_method(method):
    if isinstance(method, tuple):
        return method[0], method[1]
    else:
        return [], method

def make_rel_link(method, *args, **kwargs):
    path, qsl = validate_method_call(method, args, kwargs)
    if qsl:
        print path, qsl
        return '/%s?%s' % (path, urllib.urlencode(qsl))
    else:
        return path

def validate_method_call(method, args, kwargs):
    opt_args, method = unpack_method(method)
    req_args = filter(lambda k: k not in opt_args, method.func_code.co_varnames)
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
            print method.__module__
            path = '/'.join(method.__module__.split('.')[1:])
            print path
            return path or '/', qsl
    raise BadURL()
    
