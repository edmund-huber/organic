from helpers import optional_args

@optional_args('c')
def GET(a, b, c='opkijoij'):
    return 'a = %s, b = %s, c = %s' % (a, b, c)
