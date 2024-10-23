from flask import Flask
from flask_sqlalchemy  import SQLAlchemy
from flask_bootstrap import Bootstrap5
from .models import ouvrir_connexion

HOST = "server.hikarizsu.fr" #utilisez votre DB local si connexion impossible
USER = "root"
PASSWD = "M@RI@DBD3V"
DB = "DBMOBILIST"
PORT = 3307

app = Flask( __name__ )
app.config['BOOTSTRAP_SERVE_LOCAL'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{USER}:{PASSWD}@{HOST}:{PORT}/{DB}'
db = SQLAlchemy(app)
if db: print('DB cnx works')
Bootstrap = Bootstrap5(app)

# ENGINE = ouvrir_connexion(USER, PASSWD, HOST, DB, PORT)

# if ENGINE: print('DB cnx works')