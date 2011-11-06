def antelope():
    return 'a is for antelope. were you looking for <a href="/b">bononbo?</a>'

def bonobo():
    return 'b is for bonobo. were you looking for <a href="/a">antelope?</a>'

def home():
    return 'boring old home page'

def router(verb, path, **kwargs):
    if verb == 'GET':
        if path == ['a']:
            return antelope
        elif path == ['b']:
            return bonobo
        elif path == []:
            return home
    return None
