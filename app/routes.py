from app import app

#decarators -modifies the function that follows it
#@app.route creates an association between the URL given as
#an argument and the function.

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"
