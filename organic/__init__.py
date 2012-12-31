import urlparse

import organic.handler

def dispatch(web_path, base_templates_path, environ, start_response):

    # Choose the handler,
    web_path = filter(None, web_path.split('/'))
    url_path = filter(lambda p: '' != p, environ['PATH_INFO'].split('/'))
    h = organic.handler.choose(web_path, base_templates_path, url_path)

    # call the module.method to generate the response.
    unpack_singletons = lambda (k, v): (k, v[0] if len(v) == 1 else v)
    kwargs = dict(map(unpack_singletons, urlparse.parse_qs(environ['QUERY_STRING']).items()))
    status, headers, body = h(environ['REQUEST_METHOD'], **kwargs)
    start_response(status, headers.items())
    return body
