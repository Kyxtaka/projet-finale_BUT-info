from flask import Flask
from flask_bootstrap import Bootstrap5

app = Flask( __name__ )
app.config['BOOTSTRAP_SERVE_LOCAL'] = True
Bootstrap = Bootstrap5(app)
