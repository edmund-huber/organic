import organic.response
import organic.status

def GET():
    return organic.response.Raw(
        organic.status.OK,
        {'Content-Type': 'text/html'},
        'b is for bonobo. were you looking for <a href="/a">antelope?</a>')
