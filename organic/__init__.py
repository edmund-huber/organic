import traceback
import urlparse

import organic.handler

def dispatch(web_path, base_templates_path, is_debug, environ, start_response):

    try:
        # Find the handler and call it.
        web_path = filter(None, web_path.split('/'))
        url_path = filter(lambda p: '' != p, environ['PATH_INFO'].split('/'))
        h = organic.handler.choose(web_path, base_templates_path, environ['REQUEST_METHOD'], url_path)
        unpack_singletons = lambda (k, v): (k, v[0] if len(v) == 1 else v)
        kwargs = dict(map(unpack_singletons, urlparse.parse_qs(environ['QUERY_STRING']).items()))
        status, headers, body = h(**kwargs)

    except Exception, e:

        formatted_tb = traceback.format_exc()

        # If an error occured, we try to get the errorpage.
        try:
            h = organic.handler.choose(web_path, base_templates_path, 'GET', ['error'])
            kw = {'exception': e, 'trace': formatted_tb}
            status, headers, body = h(**kw)

        except Exception, e2:
            # Something is very wrong.
            status = organic.status.SERVER_ERROR
            headers = {'Content-Type': 'text/plain'}
            if is_debug:
                body = """***** Error while getting error page (templates/error):

%s
%s

***** Original error:

%s
%s""" % (traceback.format_exc(), repr(e2), formatted_tb, repr(e))
            else:
                body = 'Something went wrong!'

    start_response(status, headers.items())
    return body

