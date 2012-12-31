import organic.response

def GET(word='hi there'):
  return organic.response.Template('hi.html', {'word': word})
