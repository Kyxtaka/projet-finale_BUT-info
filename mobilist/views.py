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

@app.route("/avis")
def avis():
    return render_template("avis.html")

   
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
    prix_bien = FloatField('Prix neuf', validators=[DataRequired()])
    date_bien = DateField("Date de l'achat", validators=[DataRequired()])
    description_bien = TextAreaField('Description')
    justificatif_bien = FileField('Justificatif test nom')
    id_proprio = HiddenField("id_proprio")     

    def __init__(self):
        super(AjoutBienForm, self).__init__()
        self.id_proprio = current_user.id_user
        self.logement.choices = [(l.get_id_logement(), l.get_nom_logement()) for l in Proprietaire.query.get(current_user.id_user).logements]
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
            return render_template("inscription.html", form=f, present=True)
        create_user(f.mail.data, f.password.data, "proprio")
        User.modifier(f.mail.data, f.nom.data, f.prenom.data)
        return render_template("accueil_2.html")
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
    session = db.session
    form = AjoutBienForm()
    proprio = Proprietaire.query.get(current_user.id_user)
    bien = proprio.bien
    if form.validate_on_submit():
        try:
            print('entering try')
            print("is form submitted:",form.is_submitted())
            print("is submit valid:",form.validate_on_submit())
            print("if not valid:",form.errors)
            print("date_bien data:", form.date_bien)
            # print("id proprio from form:", form.id_proprio.data)
            # print("id proprio from current_user:", current_user.id_user)
            id_bien = Bien.get_max_id()+1
            nom_bien = form.nom_bien.data
            date_achat = form.date_bien.data
            id_proprio =  form.id_proprio
            print("type de date achat:",type(date_achat))
            prix = form.prix_bien.data
            id_piece = form.piece_bien.data
            id_logement = form.logement.data
            id_type = form.type_bien.data
            id_cat = form.categorie_bien.data
            # Justificatif.ajouter_justificatif(form.justificatif_bien.data, id_bien) pas encore implementé
            print("data retrieved from form")
            nouv_bien = Bien(
                id_bien=id_bien, 
                nom_bien=nom_bien, 
                date_achat=date_achat, 
                prix=prix, 
                id_proprio=id_proprio, 
                id_piece=id_piece, 
                id_logement=id_logement, 
                id_type=id_type, 
                id_cat=id_cat)
            print("nouv bien:",nouv_bien)
            session.add(nouv_bien)
            print("add bien to session")
            session.commit()
            print("success commit, check db")
            return redirect(url_for("accueil_connexion"))
        except Exception as e:
            session.rollback() # afin d eviter les erreurs de commit si une erreur est survenue
            print("is form submitted:",form.is_submitted())
            print("is submit valid:",form.validate_on_submit())
            print("if not valid:",form.errors)
            print("error ajout bien")
            print("Exception:", str(e))  # Log the exception details
            return render_template("ajout_bien.html", form=form, error=True)
    print("is form submitted:",form.is_submitted())
    print("is submit valid:",form.validate_on_submit())
    print("if not valid:",form.errors)
    if  form.is_submitted() and not form.validate_on_submit():
        print("error ajout bien")
        return render_template("ajout_bien.html", form=form, error=True)
    else:
        # print("ajout bien")
        # proprio = Proprietaire.query.get(current_user.id_user)
        # proprio.ajouter_bien(form.nom_bien.data, form.type_bien.data, form.categorie_bien.data, form.piece_bien.data, form.prix_bien.data, form.date_bien.data, form.description_bien.data, form.justificatif_bien.data)
        # return redirect(url_for("accueil_connexion"))
        return render_template("ajout_bien.html", form=form, error=False)
