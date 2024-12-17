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
import json

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

class ModificationForm(FlaskForm):
    nom = StringField('Votre nom')
    prenom = StringField('Votre Prénom')
    
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

# Endpoint pour la page d'ajout de logement
# utilise la methode POST pour l'envoi de formulaire
# utilisation du json pour la reponse (standard pour les API)
# Permet de recuperer les pieces d'un logement
@app.route("/get_pieces/<int:logement_id>")
@login_required
def get_pieces(logement_id):
    pieces = Piece.query.filter_by(id_logement=logement_id).all()
    pieces_data = [{"id": piece.get_id_piece(), "name": piece.get_nom_piece()} for piece in pieces]
    return jsonify({"pieces": pieces_data})

@app.route("/bien/ajout", methods=("GET", "POST",))
@login_required
def ajout_bien():
    form_bien = AjoutBienForm()
    if form_bien.validate_on_submit():
        try:
            print("Logs:", form_logs(form_bien))
            handle_form_bien(form_bien)
            return redirect(url_for("accueil_connexion"))
        except Exception as e:
            print("error ajout bien")
            print("Logs:", form_logs(form_bien))
            return render_template("ajout_bien.html", 
                               form=form_bien,     
                               error=True)
    return render_template("ajout_bien.html", 
                            form=form_bien, 
                            error=False)

def handle_form_bien(form_bien: AjoutBienForm):
    try:
        session = db.session
        
        id_bien = Bien.get_max_id()+1
        nom_bien = form_bien.nom_bien.data
        date_achat = form_bien.date_bien.data
        id_proprio =  form_bien.id_proprio
        prix = form_bien.prix_bien.data
        id_piece = form_bien.piece_bien.data
        id_logement = form_bien.logement.data
        id_type = form_bien.type_bien.data
        id_cat = form_bien.categorie_bien.data
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
        session.add(nouv_bien)
        session.commit()
        if form_bien.file.data:
            file_path = form_bien.create_justificatif_bien()
            print("file path:", file_path)
            process = link_justification_bien(form_bien, file_path, id_bien)
            if not process:
                raise Exception("Erreur lors de l'ajout du justificatif")
            else:
                print("Justificatif ajouté")
    except Exception as e:
        session.rollback() # afin d eviter les erreurs de commit si une erreur est survenue
        print("Logs:", form_logs(form_bien)) # affichage des logs
        print("Exception:", e)

def link_justification_bien(form: AjoutBienForm, file_path: str, id_bien: int) -> bool:
    session = db.session
    file = form.file.data
    id_justificatif = session.query(func.max(Justificatif.id_justif)).scalar() + 1
    nom_justificatif = file.filename
    date_ajout = date.today()
    url = file_path
    id_bien = id_bien
    try:
        new_justificatif = Justificatif(
            id_justif=id_justificatif,
            nom_justif=nom_justificatif,
            date_ajout=date_ajout,
            URL=url,
            id_bien=id_bien
        )
        session.add(new_justificatif)
        session.commit()
    except Exception as e:
        session.rollback()
        print("Erreur lors de l'ajout du justificatif")
        print("Exception:", e)
        return False
    return True

def form_logs(form: FlaskForm):
    print("form sumbited:",form.is_submitted())
    print("form value valid:",form.validate_on_submit())
    if isinstance(form, AjoutBienForm):
        print("Ajout bien form detected")
        if form.file.data:
            print("file name:", form.file.data.filename)
            print("file data:", form.file.data)
        else:
            print("file data is empty")
    print("form errors:",form.errors)
    print("form data:", form.data)

@app.route("/afficheLogements/", methods=("GET", "POST",))
@login_required   
def affiche_logements():
    session = db.session
    proprio = Proprietaire.query.get(current_user.id_user)
    logements = proprio.logements
    print("len logements",len(logements))
    if len(logements) == 0:
        print("Aucun logement trouvé")
        contenu = False
    else: 
        contenu = True 
    print(contenu)
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
        return render_template("afficheLogements.html", logements=logements, type_logement=type_logement, contenu=contenu)
    return render_template("afficheLogements.html", logements=logements, type_logement=type_logement, contenu=contenu)


@app.route("/simulation/", methods =("GET","POST" ,))
def simulation():
    proprio = Proprietaire.query.get(current_user.id_user)
    logements = []
    for logement in proprio.logements:
        logements.append(logement)
    return render_template("simulation.html",logements=logements)

@app.route("/mon-compte/", methods =("POST" ,"GET",))
def mon_compte():
    form=ModificationForm()
    return render_template("mon-compte.html", form=form)

@app.route("/mesBiens/", methods =["GET"])
def mesBiens():
    logement_id = request.args.get("logement")
    proprio = Proprietaire.query.get(current_user.id_user)
    logements = []
    for logement in proprio.logements:
        logements.append(logement)
    if logement_id:
        logement_actuel = int(logement_id)
        pieces = Piece.query.filter_by(id_logement=logement_actuel).all()
    else:
        logement_actuel = None
        pieces = []
    return render_template("mesBiens.html",logements=logements,logement_id=logement_id,pieces=pieces,logement_actuel=logement_actuel)

@app.route("/logement/ajout", methods =["GET","POST"])
def ajout_logement():
    session = db.session
    if request.method == "POST":
        print("Ajout logement")
        print(f"form data: {request.form}")
        logement_name = request.form.get("name")
        logement_type = request.form.get("type")
        logement_address = request.form.get("address")
        logement_description = request.form.get("description")
        try: 
            proprio = Proprietaire.query.get(current_user.id_user)
            print(f"Proprio: {proprio}")
            new_logement = create_logement(logement_name, logement_address, logement_description, logement_type, proprio)
            print(f"New logement: {new_logement}")
            rooms = json.loads(request.form.get("rooms"))
            for room in rooms:
                ajout_piece_logement(room["name"], room["desc"], new_logement)
        except Exception as e:
            session.rollback()
            print("Erreur lors de l'ajout du logement")
            print(e)
    return render_template("ajout_logement.html", type_logement=[type for type in LogementType])

def create_logement(name: str, address: str, description: str, type: str, proprio: Proprietaire):
    session = db.session
    try:
        id_logement = get_next_id(Logement)
        enum_type = LogementType[type]
        new_logement = Logement(
            id_logement = id_logement,
            nom_logement = name,
            type_logement = enum_type,
            adresse = address,
            desc_logement = description 
        )
        session.add(new_logement)
        session.commit()
        new_logement = Logement.query.get(id_logement)  
        print("Logement ajouté")
        link_logement_owner(new_logement, proprio)
    except Exception as e:
        session.rollback()
        print("Erreur lors de l'ajout du logement")
        print(e)
    return new_logement

def ajout_piece_logement(room_name: str, desc: str, Logement: Logement):
    session = db.session
    success = False
    try:
        id_piece = get_next_id(Piece)
        new_piece = Piece(
            id_piece=id_piece,
            nom_piece=room_name,
            desc_piece=desc,
            id_logement=Logement.get_id_logement()
        )
        session.add(new_piece)
        session.commit()
        print("Piece ajoutée")
        success = True
    except Exception as e:
        session.rollback()
        print("Erreur lors de l'ajout de la piece")
        print(e)
    return success

def link_logement_owner(logement: Logement, proprio: Proprietaire):
    session = db.session
    success = False
    try:
        proprio.logements.append(logement)
        session.commit()
        print("Logement lié au propriétaire")
        success = True
    except Exception as e:
        session.rollback()
        print("Erreur lors de la liaison du logement au propriétaire")
        print(e)
    return success
