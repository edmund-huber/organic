import mimetypes

import organic.response
import organic.status

def static(root, verb, path):
    fn = "%s/%s" % (root, '/'.join(path))
    return organic.response.Raw(
        organic.status.OK,
        {'Content-Type': mimetypes.guess_type(fn)[0]},
        open(fn).read())
