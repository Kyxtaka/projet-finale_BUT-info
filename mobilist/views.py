from flask import render_template
from .app import app
from flask import redirect, render_template, url_for
from wtforms import PasswordField
from .models import User
from hashlib import sha256
from flask_login import login_user , current_user, AnonymousUserMixin
from flask import request
from flask_login import login_required
from .commands import create_user
from .models import *
from .exception import *
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
    
class IncrisptionForm(FlaskForm):
    nom = StringField('Nom')
    prenom = StringField('Prénom')
    mail = StringField('Adresse e-mail')
    password = PasswordField('Mot de passe')
    next = HiddenField()
    def get_authenticated_user(self):
        user = User.query.get(self.mail.data)
        if user is None:
            return None
        m = sha256()
        m.update(self.password.data.encode())
        passwd = m.hexdigest()
        return user if passwd == user.password else None
    
class AjoutBienForm(FlaskForm):
    nom_bien = StringField('Nom du bien', validators=[DataRequired()])
    type_bien = StringField('Type de bien', validators=[DataRequired()])
    categorie_bien = StringField('Catégorie', validators=[DataRequired()])
    piece = StringField('Nombre de pièces', validators=[DataRequired()])
    prix = StringField('Prix neuf', validators=[DataRequired()])
    date = StringField("Date de l'achat", validators=[DataRequired()])
    description = StringField('Description')
    justificatif = StringField('Justificatif test nom')     
    
    
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

from flask_login import logout_user
@app.route("/logout/")
def logout():
    logout_user()
    return redirect(url_for('home'))



@app.route("/inscription/", methods=("GET", "POST",))
def inscription():
    f = IncrisptionForm()
    if not f.is_submitted():
        f.next.data = request.args.get("next")
    elif f.validate_on_submit():
        user = f.get_authenticated_user()
        if user:
            login_user(user)
            next = f.next.data or url_for("home")
            return redirect(next)
        try:
            create_user(f.mail.data, f.password.data, "proprio")
            User.modifier(f.mail.data, f.nom.data, f.prenom.data)
            return render_template("index.html")
        except:
            return render_template(
    "inscription.html", form=f, present=True)
    return render_template(
    "inscription.html", form=f, present=False)

@login_required
@app.route("/bien/ajout", methods=("GET", "POST",))
def ajout_bien():
    form = AjoutBienForm()
    if form.validate_on_submit():
        try:
            nom_bien = form.nom_bien.data
            type_bien = form.type_bien.data
            categorie_bien = form.categorie_bien.data
            piece = form.piece.data
            prix = form.prix.data
            date = form.date.data
            description = form.description.data
            justificatif = form.justificatif.data
            id_proprio = form.id_proprio.data
            nouveau_bien = (nom_bien, type_bien, categorie_bien, piece, prix, date, description, justificatif)
            # Bien.ajouter(form.nom_bien.data, form.type_bien.data, form.categorie_bien.data, form.piece.data, form.prix.data, form.date.data, form.description.data, form.justificatif.data)
            return render_template("index.html")
        except:
            return render_template("ajout_bien.html", present=True)
    return render_template("ajout_bien.html")

