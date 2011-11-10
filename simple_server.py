from wsgiref.simple_server import make_server

import organic

httpd = make_server('', 8000, organic.dispatch)
httpd.serve_forever()
