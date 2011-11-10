from organic.helpers import make_rel_link

import app.z

def GET(opt='narf'):
    return "%s! here's a <a href=\"%s\">link</a>" % (opt, make_rel_link(app.z, 7, 9, c='aaaaaaa'))
