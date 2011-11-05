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

to make a dynamic path, for example matching any page like
/rage/fuuuuuUUUuuuuuuuUU , create an app/rage.py ,

```python
import re

def rage():
    return 'rawwwrrr!'

def router(verb, path, **kwargs):
    if verb == 'GET':
        if len(path) == 2 and re.search('^[Ff]+[Uu]*$', path[1]):
            return rage
    return None
```

or, for example, to serve /a and /b , create an app/__init__.py ,

```python
def antelope():
    return 'a is for antelope. were you looking for <a href="/b">bononbo?</a>'

def bonobo():
    return 'b is for bonobo. were you looking for <a href="/a">antelope?</a>'

def router(verb, path, **kwargs):
    if verb == 'GET':
        if path == ['a']:
            return antelope
        elif path == ['b']:
            return bonobo
    return None
```

note that I haven't figured out a clever way to expose URLs available
through custom routers.