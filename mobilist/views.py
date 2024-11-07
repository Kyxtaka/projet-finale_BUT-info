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

@app.route("/accueil")
def accueil():
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
    
@app.route("/accueil-connexion/")
def accueil_connexion():
    return render_template("accueil_2.html")
    
@app.route("/login/", methods =("GET","POST" ,))
def login():
    f = LoginForm()
    if not f.is_submitted():
        f.next.data = request.args.get("next")
    elif f.validate_on_submit():
        user = f.get_authenticated_user()
        if user:
            print("test2")
            login_user(user)
            next = f.next.data or url_for("accueil_connexion")
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
  


@app.route("/information")
def information():
    return render_template("information.html")


@app.route("/services")
def services():
    return render_template("services.html")

@app.route("/afficheLogements/")
def affiche_logements():
    session = db.session
    proprio = Proprietaire.query.get(current_user.id_user)
    logements = proprio.logements
    print(logements)
    if request.method == "GET": #utilisation de request car pas envie d'utiliser les méthodes de flask, car j utilise JS
        print("recerption de la requete")
        form_type = request.args.get("type-form")
        match form_type:
            case "DELETE_LOGEMENT":
                print("DELETE_LOGEMENT")
                id_logement = request.args.get("id")
                logement = Logement.query.get(id_logement)
                print("logement recupere",logement)
                try :
                    session.delete(logement)
                    session.commit()
                except Exception as e:
                    session.rollback()
                    print("Erreur lors de la suppression du logement")
                    print(e)
            case "UPDATE_LOGEMENT":
                print("UPDATE_LOGEMENT")
                id_logement = request.args.get("id")
                logement = Logement.query.get(id_logement)
                print("logement recupere",logement)
                name = request.args.get("name")
                address = request.args.get("address")
                description = request.args.get("description")
                print("values",name,address,description)
                logement.set_nom_logement(name)
                logement.set_adresse_logement(address)
                logement.set_desc_logement(description)
                print("logement apres modif",logement)
                session.commit()
                # return render_template("updateLogement.html", logement=logement)
        proprio = Proprietaire.query.get(current_user.id_user)
        logements = proprio.logements
        return render_template("afficheLogements.html", logements=logements)
    return render_template("afficheLogements.html", logements=logements)