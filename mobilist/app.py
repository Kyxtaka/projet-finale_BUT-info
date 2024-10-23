from flask import Flask
from flask_sqlalchemy  import SQLAlchemy
from flask_bootstrap import Bootstrap5
from constante import *
from secure_constante import * 
import os


def mkpath (p):
    return os.path.normpath(
        os.path.join(os.path.dirname(__file__ ),p)
    )

app = Flask( __name__ )
app.config['BOOTSTRAP_SERVE_LOCAL'] = True
# app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{USER}:{PASSWD}@{HOST}:{PORT}/{DB}'
app.config['SQLALCHEMY_DATABASE_URI'] = ('sqlite:///'+mkpath('../myapp.db')) #marche actuellement
db = SQLAlchemy(app)
if db: print('DB cnx works')
Bootstrap = Bootstrap5(app)