from .app import app
from flask import redirect, render_template, url_for

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login")
def connexion():
    return render_template("connexion.html")


@app.route("/inscription")
def inscription():
    return render_template("inscription.html")