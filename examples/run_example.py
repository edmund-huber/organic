# for example, `python run_example.py a_or_b`

import functools
import organic
import sys
import wsgiref.simple_server

wsgi_app = functools.partial(organic.dispatch, sys.argv[1])
httpd = wsgiref.simple_server.make_server('', 8000, wsgi_app)
httpd.serve_forever()
