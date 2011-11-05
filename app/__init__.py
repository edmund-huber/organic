from helpers import make_rel_link

import app.test

def GET():
    return "this is just my boring home page<br>\
here's a <a href=\"%s\">link</a>" % make_rel_link(app.test.GET, 7, 9, c='aaaaaaa')
