from helpers import optional_args, make_rel_link

import app.z

@optional_args('opt')
def GET(opt='narf'):
    return "%s! here's a <a href=\"%s\">link</a>" % (opt, make_rel_link(app.z.GET, 7, 9, c='aaaaaaa'))
