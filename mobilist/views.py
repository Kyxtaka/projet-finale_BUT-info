from flask import render_template
from .app import app
from flask import redirect, render_template, url_for
from wtforms import PasswordField
from .models import User
from hashlib import sha256
from flask_login import login_user , current_user, AnonymousUserMixin
from flask import request
from flask_login import login_required

from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField
from wtforms.validators import DataRequired

@app.route("/")
def home():
    return render_template('accueil.html')

   
class LoginForm(FlaskForm):
    mail = StringField('Adresse e-mail')
    password = PasswordField('Mot de passe')
    next = HiddenField()
    id = HiddenField()
    def get_authenticated_user(self):
        user = User.query.get(self.mail.data)
        if user is None:
            return None
        m = sha256()
        m.update(self.password.data.encode())
        passwd = m.hexdigest()
        return user if passwd == user.password else None

@app.route("/login/", methods =("GET","POST" ,))
def login():
    f = LoginForm()
    if not f.is_submitted():
        f.next.data = request.args.get("next")
    elif f.validate_on_submit():
        user = f.get_authenticated_user()
        if user:
            login_user(user)
            next = f.next.data or url_for("home")
            return redirect(next)
    return render_template(
    "connexion.html",
    form=f)
    
@app.route("/avis")
def avis():
    return render_template("avis.html")

from flask_login import logout_user
@app.route("/logout/")
def logout():
    logout_user()
    return redirect(url_for('home'))



@app.route("/inscription")
def inscription():
    return render_template("inscription.html")
