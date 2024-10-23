from .app import app

@app.route("/")
def home():
    return "<h1> MobiList arrive ...</h1>"