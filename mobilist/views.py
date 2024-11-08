from datetime import datetime
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
from werkzeug.utils import secure_filename
from werkzeug.datastructures import MultiDict

#constante : chemin d'acces au dossier de telechargement des justificatifs
UPLOAD_FOLDER_JUSTIFICATIF = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 
    app.config['UPLOAD_FOLDER'], 
    'justificatifs'
)

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
    
class UploadFileForm(FlaskForm):
    file = FileField('File', validators=[DataRequired()])

    def __init__(self,*args, **kwargs):
        super(UploadFileForm, self).__init__(*args, **kwargs)
        #########################################################
        # print(f"**********************************\n {self.file.validators} \n**********************************")
        # if self.validate_file_format not in self.file.validators:
        #     self.file.validators = (self.validate_file_format,) +  tuple(self.file.validators)
        # print(f"**********************************\n {self.file.validators} \n**********************************")
        #########################################################

    def validate_file_format(self, form, field):
            filename = field.data
            print("form:", form)
            print("field:", field)
            print("field.data:", field.data)
            
            if filename:
                print("filname:", filename)
                if not (filename.endswith(".pdf") or filename.endswith(".png") or filename.endswith(".jpg") or filename.endswith(".jpeg")):
                    raise ValidationError("Le fichier doit être de type PDF, PNG, JPG ou JPEG")
                elif len(filename) > 50:
                    raise ValidationError("Le nom du fichier est trop long")
            else:
                raise ValidationError("Le fichier est vide")

    def validate_file_size(self, form, field):
        file = field.data
        if file:
            if len(file.read()) > 1000000:
                raise ValidationError("Le fichier est trop volumineux")
        else:
            raise ValidationError("Le fichier est vide")  
        
    def create_justificatif_bien(self):
        try:
            file = self.file.data
            file.save(os.path.join(UPLOAD_FOLDER_JUSTIFICATIF, secure_filename(file.filename)))
            print("file saved")
        except Exception as e:
            print("erreur:", e)

class AjoutBienForm(FlaskForm):
    logement  = SelectField('Logement', validators=[DataRequired()])
    nom_bien = StringField('Nom du bien', validators=[DataRequired()])
    type_bien = SelectField('Type de bien', validators=[DataRequired()])
    categorie_bien = SelectField('Catégorie', validators=[DataRequired()])
    piece_bien = SelectField('Nombre de pièces', validators=[DataRequired()])
    prix_bien = FloatField('Prix neuf', validators=[DataRequired()])
    date_bien = DateField("Date de l'achat", validators=[DataRequired()])
    description_bien = TextAreaField('Description')
    file = FileField('File')
    id_proprio = HiddenField("id_proprio") 

    def __init__(self,*args, **kwargs):
        super(AjoutBienForm, self).__init__(*args, **kwargs)
        self.id_proprio = current_user.id_user
        self.logement.choices = [(l.get_id_logement(), l.get_nom_logement()) for l in Proprietaire.query.get(current_user.id_user).logements]
        self.type_bien.choices = [(t.id_type, t.nom_type) for t in TypeBien.query.all()]
        self.categorie_bien.choices = [(c.get_id_cat(), c.get_nom_cat()) for c in Categorie.query.all()]
        self.piece_bien.choices = [(p.get_id_piece(), p.get_nom_piece()) for p in Piece.query.all()]

    def create_justificatif_bien(self) -> str:
        try:
            file = self.file.data
            if not os.path.exists(os.path.join(UPLOAD_FOLDER_JUSTIFICATIF, str(current_user.id_user))): # creation du dossier de l'utilisateur si inexistant
                os.makedirs(os.path.join(UPLOAD_FOLDER_JUSTIFICATIF, str(current_user.id_user)))
            CUSTOM_UPLOAD_FOLDER_JUSTIFICATIF = os.path.join(UPLOAD_FOLDER_JUSTIFICATIF, str(current_user.id_user))
            file.save(os.path.join(CUSTOM_UPLOAD_FOLDER_JUSTIFICATIF, secure_filename(file.filename)))
            print("file saved")
            return os.path.join(CUSTOM_UPLOAD_FOLDER_JUSTIFICATIF, file.filename) # retourne le chemin du fichier, pour l'enregistrement en BD
        except Exception as e:
            print("erreur:", e)
        

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
    
@app.route("/avis")
def avis():
    return render_template("avis.html")

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


@app.route("/afficheLogements/", methods=("GET", "POST",))
@login_required   
def affiche_logements():
    session = db.session
    proprio = Proprietaire.query.get(current_user.id_user)
    logements = proprio.logements
    type_logement = [type for type in LogementType]
    print
    print(logements)
    if request.method == "POST": #utilisation de request car pas envie d'utiliser les méthodes de flask, car j utilise JS
        print("recerption de la requete")
        form_type = request.form.get("type-form")
        print("form_type",form_type)
        match form_type:
            case "DELETE_LOGEMENT":
                try :
                    print("DELETE_LOGEMENT")
                    id_logement = request.form.get("id")
                    logement = Logement.query.get(id_logement)
                    print("logement recupere",logement)
                    session.delete(logement)
                    session.commit()
                    print("Logement supprimé")
                except Exception as e:
                    session.rollback()
                    print("Erreur lors de la suppression du logement")
                    print(e)
            case "UPDATE_LOGEMENT":
                try:
                    print("UPDATE_LOGEMENT")
                    id_logement = request.form.get("id")
                    logement = Logement.query.get(id_logement)
                    print("logement recupere",logement)
                    name = request.form.get("name")
                    address = request.form.get("address")
                    description = request.form.get("description")
                    type = request.form.get("type")
                    enum_type = LogementType[type]
                    print("values",name,address,description, type, enum_type)
                    logement.set_nom_logement(name)
                    logement.set_adresse_logement(address)
                    logement.set_desc_logement(description)
                    logement.set_type_logement(enum_type)
                    print("logement apres modif",logement)
                    session.commit()
                    print("Logement modifié")
                except Exception as e:
                    session.rollback()
                    print("Erreur lors de la modification du logement")
                    print(e)
                # return render_template("updateLogement.html", logement=logement)
        proprio = Proprietaire.query.get(current_user.id_user)
        logements = proprio.logements
        return render_template("afficheLogements.html", logements=logements, type_logement=type_logement)
    return render_template("afficheLogements.html", logements=logements, type_logement=type_logement)
