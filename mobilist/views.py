from flask import jsonify, render_template
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
from wtforms import * #import de tous les champs
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

class AjoutBienForm(FlaskForm):
    logement  = SelectField('Logement', validators=[DataRequired()])
    nom_bien = StringField('Nom du bien', validators=[DataRequired()])
    type_bien = SelectField('Type de bien', validators=[DataRequired()])
    categorie_bien = SelectField('Catégorie', validators=[DataRequired()])
    piece_bien = SelectField('Nombre de pièces', validators=[DataRequired()])
    prix_bien = StringField('Prix neuf', validators=[DataRequired()])
    date_bien = DateTimeField("Date de l'achat", validators=[DataRequired()])
    description_bien = TextAreaField('Description')
    justificatif_bien = FileField('Justificatif test nom')
    id_proprio = HiddenField()     

    def __init__(self):
        super(AjoutBienForm, self).__init__()
        id_proprio = current_user.id_user
        self.logement.choices = [(l.get_id_logement(), l.get_nom_logement()) for l in Proprietaire.query.get(id_proprio).logements]
        self.type_bien.choices = [(t.id_type, t.nom_type) for t in TypeBien.query.all()]
        self.categorie_bien.choices = [(c.get_id_cat(), c.get_nom_cat()) for c in Categorie.query.all()]
        self.piece_bien.choices = [(p.get_id_piece(), p.get_nom_piece()) for p in Piece.query.all()]
 
@app.route("/accueil-connexion/")
@login_required   
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

@app.route("/afficheLogements")
@login_required   
def affiche_logements():
    proprio = Proprietaire.query.get(current_user.id_user)
    logements = proprio.logements
    print(logements)
    return render_template("afficheLogements.html", logements=logements)


# Obtention des pièces d'un logement pour le form interactive ajout legement et retour data en json
# permet une meilleur dynamique pour la gestion de la page avec javascript 
@app.route("/get_pieces/<int:logement_id>")
@login_required
def get_pieces(logement_id):
    pieces = Piece.query.filter_by(id_logement=logement_id).all()
    pieces_data = [{"id": piece.get_id_piece(), "name": piece.get_nom_piece()} for piece in pieces]
    return jsonify({"pieces": pieces_data})

@app.route("/bien/ajout", methods=("GET", "POST",))
@login_required
def ajout_bien():
    form = AjoutBienForm()
    if form.validate_on_submit():
        try:
            print('blabla')
            return render_template("index.html")
        except:
            print("error ajout bien")
            return render_template("ajout_bien.html", form=form)
    return render_template("ajout_bien.html", form=form)
