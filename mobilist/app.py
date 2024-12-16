from flask import Flask
from flask_sqlalchemy  import SQLAlchemy
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
# from .secure_constante import *
import os

def mkpath (p):
    return os.path.normpath(
        os.path.join(os.path.dirname(__file__ ),p)
    )
from flask_bootstrap import Bootstrap5

app = Flask( __name__ )
app.config['BOOTSTRAP_SERVE_LOCAL'] = True # configuration avec bootstrap
app.config['TESTING'] = False
app.config['SECRET_KEY'] = "1f371826-9114-495d-bde8-0fd605e6356d"
# app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{USER}:{PASSWD}@{HOST}:{PORT}/{DB}' #Serveur distant de BD (probleme de driver)

app.config['SQLALCHEMY_DATABASE_URI'] = ('sqlite:///'+mkpath('../DBMOBILIST.db')) #Fichier DB actuelle (solution fonctionnelle)
db = SQLAlchemy(app)
print('working on DBMOBILIS') 
Bootstrap = Bootstrap5(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
