import mimetypes
import mako.template
import os.path

import organic.response
import organic.status

def custom(lookup, module, path, method, **params):
    return interpret(lookup, module, module.router(method, path, **params))

def default(lookup, module, method, **params):
    if hasattr(module, method):
        return interpret(lookup, module, getattr(module, method)(**params))
    else:
        return _404()

def interpret(lookup, module, v):
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
            return _500()

    elif isinstance(v, organic.response.Raw):
        if 'Content-Type' not in v.headers:
            return _500()
        else:
            return v.status, v.headers, v.body

    elif v is None:
        return _404()

    else:
        return _500()
