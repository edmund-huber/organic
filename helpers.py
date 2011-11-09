import urllib

def make_rel_link(method, *args, **kwargs):
    path, qsl = validate_method_call(method, args, kwargs)
    if qsl:
        return '/%s?%s' % (path, urllib.urlencode(qsl))
    else:
        return path
