from wsgiref.simple_server import make_server

import example

httpd = make_server('', 8000, example.dispatch)
httpd.serve_forever()
