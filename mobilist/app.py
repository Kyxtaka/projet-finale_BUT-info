from flask import Flask
from flask_bootstrap import Bootstrap5
from .models import ouvrir_connexion

HOST = "server.hikarizsu.fr" #utilisez votre DB local si connexion impossible
USER = "root"
PASSWD = "M@RI@DBD3V"
DB = "DBMOBILIST"
PORT = 3307

app = Flask( __name__ )
app.config['BOOTSTRAP_SERVE_LOCAL'] = True
Bootstrap = Bootstrap5(app)

ENGINE = ouvrir_connexion(USER, PASSWD, HOST, DB, PORT)
if ENGINE: print('DB cnx works')