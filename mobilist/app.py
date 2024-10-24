from flask import Flask
from flask_sqlalchemy  import SQLAlchemy
from flask_bootstrap import Bootstrap5
from .constante import *

import os
from flask_login import LoginManager


def mkpath (p):
    return os.path.normpath(
        os.path.join(os.path.dirname(__file__ ),p)
    )
from flask_bootstrap import Bootstrap5

app = Flask( __name__ )
# configuration avec bootstrap
app.config['BOOTSTRAP_SERVE_LOCAL'] = True
# app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{USER}:{PASSWD}@{HOST}:{PORT}/{DB}'
app.config['SQLALCHEMY_DATABASE_URI'] = ('sqlite:///'+mkpath('../DBMOBILIST.db')) #marche actuellement
db = SQLAlchemy(app)
if db: print('working on DBMOBILIS')
Bootstrap = Bootstrap5(app)



login_manager = LoginManager(app)
login_manager.login_view = "login"
