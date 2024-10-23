from flask import Flask
from flask_bootstrap import Bootstrap5

app = Flask( __name__ )
# configuration avec bootstrap
app.config['BOOTSTRAP_SERVE_LOCAL'] = True
bootstrap = Bootstrap5(app)