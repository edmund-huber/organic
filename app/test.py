from helpers import optional_args, make_rel_link

import app

@optional_args('c')
def GET(a, b, c='jabbermocky'):
    return 'a = %s<br>\
b = %s<br>\
c = %s<br>\
<a href="%s">link</a> back home.' % (a, b, c, make_rel_link(app.GET))
