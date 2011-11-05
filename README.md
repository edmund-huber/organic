to run on a reference wsgi-compliant httpd,

    python simple_server.py

to create a method, say GET /a/b/c ,

    mkdir -p app/a/b
    touch app/a/__init__.py
    touch app/a/b/__init__.py
    echo "def GET(): return 'herro'" > app/a/b/c.py

(the following is equivalent)

    mkdir -p app/a/b/c
    touch app/a/__init__.py
    touch app/a/b/__init__.py
    echo "def GET(): return 'herro'" > app/a/b/c/__init__.py

to have required query arguments, say GET /a/b/c?thing=3 ,

    echo "def GET(thing): return 'the thing is: %s' % thing" > app/a/b/c.py

to have optional query arguments, say GET /a/b/c or /a/b/c?opt=meow ,

```python
from helpers import optional_args

@optional_args('opt')
def GET(opt='narf'):
    return 'optionally: %s' % opt
```

to make a link, say to another page /z with some arguments,

```python
from helpers import optional_args, make_rel_link

import app.z

@optional_args('opt')
def GET(opt='narf'):
    return "%s! here's a <a href=\"%s\">link</a>" % (opt, make_rel_link(app.z.GET, 7, 9, c='aaaaaaa'))
```

to make a dynamic path, for example matching /a/fu , /a/fuu ,
/a/fUUuu/ , etc , create app/a/__init__.py ,

```python


```