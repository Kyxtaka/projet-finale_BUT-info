
from flask import jsonify, render_template
from .app import app
from flask import redirect, render_template, url_for, render_template_string
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
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import spacy
from PyPDF2 import PdfReader
from .secure_constante import GOOGLE_SMTP, GOOGLE_SMTP_PWD, GOOGLE_SMTP_USER
import ast


nlp = spacy.load("fr_core_news_md")

from flask import send_file
from reportlab.pdfgen import canvas #pip install reportlab
from datetime import date
from datetime import datetime
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))

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

class ResetPasswordFrom(FlaskForm):
    mdp = PasswordField("Mot de passe")
    valider = PasswordField("Confirmer mot de passe")


class ModificationForm(FlaskForm):
    nom = StringField('Votre Nom')
    prenom = StringField('Votre Prénom')
    mail = StringField('Votre Adresse e-mail')
    

class ResetForm(FlaskForm):
    email = StringField("Votre email")

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


    def lire_pdf(self,fichier):
        reader = PdfReader(fichier)
        texte = ""
        for page in reader.pages:
            texte += page.extract_text()
        return texte

class AjoutBienForm(FlaskForm):
    logement  = SelectField('Logement', validators=[DataRequired()], coerce=int)
    nom_bien = StringField('Nom du bien', validators=[DataRequired()])
    type_bien = SelectField('Type de bien', validators=[DataRequired()],coerce=int)
    categorie_bien = SelectField('Catégorie', validators=[DataRequired()], coerce=int)
    piece_bien = SelectField('Nombre de pièces', validators=[DataRequired()], coerce=int)
    prix_bien = FloatField('Prix neuf', validators=[DataRequired()])
    date_bien = DateField("Date de l'achat", validators=[DataRequired()])
    description_bien = TextAreaField('Description')
    file = FileField('File')
    id_proprio = HiddenField("id_proprio") 
    id_bien = HiddenField("id_proprio")

    def __init__(self,*args, **kwargs):
        super(AjoutBienForm, self).__init__(*args, **kwargs)
        self.id_bien = None
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
    
    def set_id(self,id):
        self.id_bien = id
    def get_log_choices(self,nom):
        for elem in self.logement.choices:
            if elem[1]==nom:
                return elem[0]
        return ""

    def get_type_bien_choices(self, nom):
        for elem in self.type_bien.choices:
            if elem[1]==nom:
                return elem[0]
        return ""
    
    def get_cat_bien_choices(self, nom):
        for elem in self.categorie_bien.choices:
            if elem[1]==nom:
                return elem[0]
        return ""
    
    def __str__(self):
        return "Form Bien, values :"+self.nom_bien.data

def generate_pdf_tous_logements(proprio,logements) -> BytesIO:
    buffer = BytesIO()
    canva = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 2 * cm
    # Fonction qui dessine des blocs gris avec du texte
    def draw_grey_box_with_text(canva, x, y, width, height, text, font="Helvetica", font_size=13):
        canva.setFillColorRGB(0.827, 0.827, 0.827)
        canva.rect(x, y, width, height, fill=1, stroke=0)
        canva.setFillColorRGB(0, 0, 0)
        canva.setFont(font, font_size)
        canva.drawString(x + 5, y + height / 2 - font_size / 2, text)
    # Titre 
    canva.setFillColorRGB(0.38, 0.169, 0.718)
    canva.setFont("Helvetica-Bold", 20)
    canva.drawCentredString(width / 2, y, "INVENTAIRE DES BIENS")
    y -= 1 * cm
    # Sous-titre
    canva.setFillColorRGB(0, 0, 0)
    canva.setFont("Helvetica-Bold", 15)
    canva.drawCentredString(width / 2, y, f"en date du {date.today()}")
    y -= 1.5 * cm
    # Valeur totale
    # func.sum(Bien.prixtotal_valeur
    #list_bien = db.session.query(Bien).filter_by(id_proprio=proprio.id_proprio)
    #total_valeur = 0
    #for bien in list_bien:
    #    print(bien.__repr__())
    #    total_valeur += db.session.query(Bien.prix).filter_by(id_bien=bien.id_bien).scalar()

    total_valeur = db.session.query(func.sum(Bien.prix)).filter(Bien.id_proprio == proprio.id_proprio).scalar()
    if total_valeur == None:
        total_valeur = 0
    print(total_valeur)
    # db.session.query(Logement).filter_by(id_logement=logement_id).first().adresse

    canva.setFillColorRGB(0.792, 0.659, 1)
    canva.rect(20, y, width - 40, 1 * cm, fill=1, stroke=0)
    canva.setFillColorRGB(0, 0, 0)
    canva.setFont("Helvetica-Bold", 12)
    canva.drawString(25, y + 8, f"VALEUR TOTALE ESTIMÉE DE TOUS LES BIENS : {total_valeur} €")
    y -= 1.5 * cm
    # Informations
    height_box = 1 * cm
    draw_grey_box_with_text(canva, 20, y-3, width - 40, height_box, f"NOM : {proprio.get_nom()} {proprio.get_prenom()}")
    y -= height_box
    draw_grey_box_with_text(canva, 20, y-6, width - 40, height_box, f"MAIL : {proprio.get_mail()}")
    y -= height_box
    draw_grey_box_with_text(canva, 20, y-9, width - 40, height_box, f"ANNÉE DU SINISTRE : {datetime.now().year}")
    y -= height_box
    # Parcours des pièces et des biens
    for loge in logements:
        if y < 3 * cm:
            canva.showPage()
            y = height - 2 * cm
        canva.setFont("Helvetica-Bold", 13)
        canva.drawString(1 * cm, y, f"{loge.nom_logement} ({loge.adresse})")
        y -= 1 * cm
        pieces = db.session.query(Piece).filter_by(id_logement=loge.id_logement).all()
        for p in pieces:
            if y < 3 * cm:  # Saut de page si besoin
                canva.showPage()
                y = height - 2 * cm
            canva.setFont("Helvetica-Bold", 12)
            canva.drawString(1 * cm, y, f"{p.get_nom_piece()}")
            y -= 0.7 * cm
            biens = db.session.query(Bien, Categorie).join(Categorie, Bien.id_cat == Categorie.id_cat) \
                .filter(Bien.id_piece == p.id_piece).all()
            biens_par_categorie = {}
            for bien, categorie in biens:
                biens_par_categorie.setdefault(categorie.nom_cat, []).append((bien.nom_bien, bien.prix))
            for cat, items in biens_par_categorie.items():
                canva.setFont("Helvetica-Bold", 11)
                canva.drawString(2 * cm, y, f"{cat}")
                y -= 0.5 * cm
                canva.setFont("Helvetica", 10)
                for nom_bien, prix in items:
                    canva.drawString(3 * cm, y, f"- {nom_bien}")
                    canva.drawRightString(width - 2 * cm, y, f"{prix} €")
                    y -= 0.5 * cm
                    if y < 3 * cm:  # Saut de page si besoin
                        canva.showPage()
                        y = height - 2 * cm
                y -= 0.5 * cm  # Espace entre catégories
            # Ligne de fin
            canva.line(1 * cm, y, width - 2 * cm, y)
            y -= 1 * cm        
    canva.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="inventaire_biens.pdf", mimetype="application/pdf")

@app.route("/accueil-connexion/", methods =("GET","POST" ,))
@login_required   
def accueil_connexion():
    infos, a_justifier = biens()
    return render_template("accueil_2.html", infos=infos[:4], justifies=a_justifier[:4])

def biens():
    biens, justifies = User.get_biens_by_user(current_user.mail)
    infos = []
    for elem in biens:
        for j in range(len(elem)):
            bien = elem[j]
            justif = bien.get_justif(bien.id_bien)
            if justif == None:
                justif= "Aucun"
            infos.append([bien.nom_bien, bien.get_nom_logement_by_bien(bien.id_bien).nom_logement, bien.get_nom_piece_by_bien(bien.id_bien).nom_piece, str(bien.id_bien),justif])
    a_justifier = []
    for justifie in justifies:
        a_justifier.append([justifie.nom_bien, justifie.get_nom_logement_by_bien(justifie.id_bien).nom_logement, justifie.get_nom_piece_by_bien(justifie.id_bien).nom_piece, str(justifie.id_bien)])
    return infos, a_justifier
    
@app.route("/login/", methods =("GET","POST" ,))
def login() -> str:
    f = LoginForm()
    if not f.is_submitted():
        f.next.data = request.args.get("next")
    elif f.validate_on_submit():
        user = f.get_authenticated_user()
        if user:
            login_user(user)
            next = f.next.data or url_for("accueil_connexion")
            return redirect(next)
        return render_template(
        "connexion.html",
        form=f,mdp=False)
    return render_template(
    "connexion.html",
    form=f,mdp=True)

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

@app.route("/ensemblebiens/", methods=["GET"])
@login_required
def ensemble_biens():
    info, justifie = biens()
    return render_template("ensemble_biens.html", infos=info, justifies=justifie)
    
def handle_form_bien(form_bien: AjoutBienForm):
    try:
        session = db.session

        id_bien = Bien.next_id()+1
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
    id_justificatif = Justificatif.next_id()
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
    if len(logements) == 0:
        print("Aucun logement trouvé")
        contenu = False
    else:
        contenu = True
    type_logement = [type for type in LogementType]
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
                    logement.delete(Proprietaire.query.get(current_user.id_user))
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

def generate_pdf(proprio,logement_id,sinistre_annee,sinistre_type) -> BytesIO:
    buffer = BytesIO()
    canva = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 2 * cm
    # Fonction qui dessine des blocs gris avec du texte
    def draw_grey_box_with_text(canva, x, y, width, height, text, font="Helvetica", font_size=13):
        canva.setFillColorRGB(0.827, 0.827, 0.827)
        canva.rect(x, y, width, height, fill=1, stroke=0)
        canva.setFillColorRGB(0, 0, 0)
        canva.setFont(font, font_size)
        canva.drawString(x + 5, y + height / 2 - font_size / 2, text)
    # Titre 
    canva.setFillColorRGB(0.38, 0.169, 0.718)
    canva.setFont("Helvetica-Bold", 20)
    canva.drawCentredString(width / 2, y, "INVENTAIRE DES BIENS")
    y -= 1 * cm
    # Sous-titre
    canva.setFillColorRGB(0, 0, 0)
    canva.setFont("Helvetica-Bold", 15)
    canva.drawCentredString(width / 2, y, f"en date du {date.today()}")
    y -= 1.5 * cm
    # Valeur totale
    total_valeur = db.session.query(func.sum(Bien.prix)).filter(Bien.id_logement == logement_id).scalar()
    if total_valeur == None:
        total_valeur = 0
    canva.setFillColorRGB(0.792, 0.659, 1)
    canva.rect(20, y, width - 40, 1 * cm, fill=1, stroke=0)
    canva.setFillColorRGB(0, 0, 0)
    canva.setFont("Helvetica-Bold", 12)
    canva.drawString(25, y + 8, f"VALEUR TOTALE ESTIMÉE DE TOUS LES BIENS : {total_valeur} €")
    y -= 1.5 * cm
    # Informations
    height_box = 1 * cm
    draw_grey_box_with_text(canva, 20, y-3, width - 40, height_box, f"NOM : {proprio.get_nom()} {proprio.get_prenom()}")
    y -= height_box
    draw_grey_box_with_text(canva, 20, y-6, width - 40, height_box, f"MAIL : {proprio.get_mail()}")
    y -= height_box
    adresse = db.session.query(Logement).filter_by(id_logement=logement_id).first().adresse
    draw_grey_box_with_text(canva, 20, y-9, width - 40, height_box, f"ADRESSE DU LOGEMENT : {adresse}")
    y -= height_box
    draw_grey_box_with_text(canva, 20, y-12, width - 40, height_box, f"ANNÉE DU SINISTRE : {sinistre_annee}")
    y -= height_box
    draw_grey_box_with_text(canva, 20, y-15, width - 40, height_box, f"TYPE DE SINISTRE : {sinistre_type}")
    y -= 1.5 * cm
    # Parcours des pièces et des biens
    pieces = db.session.query(Piece).filter_by(id_logement=logement_id).all()
    for p in pieces:
        if y < 3 * cm:  # Saut de page si besoin
            canva.showPage()
            y = height - 2 * cm
        canva.setFont("Helvetica-Bold", 12)
        canva.drawString(1 * cm, y, f"{p.get_nom_piece()}")
        y -= 0.7 * cm
        biens = db.session.query(Bien, Categorie).join(Categorie, Bien.id_cat == Categorie.id_cat) \
            .filter(Bien.id_piece == p.id_piece).all()
        biens_par_categorie = {}
        for bien, categorie in biens:
            biens_par_categorie.setdefault(categorie.nom_cat, []).append((bien.nom_bien, bien.prix))
        for cat, items in biens_par_categorie.items():
            canva.setFont("Helvetica-Bold", 11)
            canva.drawString(2 * cm, y, f"{cat}")
            y -= 0.5 * cm
            canva.setFont("Helvetica", 10)
            for nom_bien, prix in items:
                canva.drawString(3 * cm, y, f"- {nom_bien}")
                canva.drawRightString(width - 2 * cm, y, f"{prix} €")
                y -= 0.5 * cm
                if y < 3 * cm:  # Saut de page si besoin
                    canva.showPage()
                    y = height - 2 * cm
            y -= 0.5 * cm  # Espace entre catégories
        # Ligne de fin
        canva.line(1 * cm, y, width - 2 * cm, y)
        y -= 1 * cm        
    canva.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="inventaire_biens.pdf", mimetype="application/pdf")


@app.route("/simulation/", methods =("GET","POST" ,))
def simulation():
    proprio = Proprietaire.query.get(current_user.id_user)
    logements = []
    for logement in proprio.logements:
        logements.append(logement)
    logement_id = request.form.get('logement_id')
    sinistre_annee = request.form.get('sinistre_annee')
    sinistre_type = request.form.get('sinistre_type')

    # Message d'erreur si tous les champs ne sont pas sélectionnés
    if request.method == "POST":
        if not logement_id or not sinistre_annee or not sinistre_type:
            message = "Veuillez sélectionner tous les champs."
            return render_template("simulation.html", logements=logements,
                                   message=message, logement_id=logement_id,
                                   sinistre_annee=sinistre_annee,
                                   sinistre_type=sinistre_type)
        return generate_pdf(proprio,logement_id,sinistre_annee,sinistre_type)
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

@app.route("/forgotPassword/", methods=["POST", "GET"])
def page_oublie():
    form = ResetForm()
    tentative = None
    if form.is_submitted():
        tentative = False
        user = User.get_by_mail(form.email.data)
        if user != None:
            genrated_token = ChangePasswordToken(user.get_id()) # generation du token avec validite de 10min par default
            try: 
                db.session.add(genrated_token)
                db.session.commit()
                tentative = True
                status = send_change_pwd_email(form.email.data, genrated_token.get_token())
            except Exception as e:
                print("Erreur lors de la sauvegarde du token")
                print(e)
                tentative = True
    if tentative is None:
        return render_template("mdp_oublie.html", tentative=False, form=form)
    elif not tentative:
        return render_template("mdp_oublie.html", tentative=True, form=form)
    else:
        return render_template("envoi_email.html", email=form.email.data)

@app.route("/forgotPassword/setPassword", methods=["POST", "GET"])
def set_password_page():
    valid_access = False
    if request.args.get("token"):
        token = request.args.get("token")
        tokenObject = ChangePasswordToken.get_by_token(token)
        if tokenObject is None:
            valid_access = False
        else:
            valid_access = not tokenObject.is_expired()
            print(f"token: {token}")
            print(f"is expired: {tokenObject.is_expired()}")
            print(f"valid_access: {valid_access}")
    if not valid_access:
        return render_template(f"unauthorized_access.html"), 401
    user = User.get_by_mail(ChangePasswordToken.get_by_token(token).get_email())
    form = ResetPasswordFrom()
    if form.is_submitted():
        if form.mdp.data == form.valider.data:
            user.set_password(form.mdp.data)
            tokenObject.set_used()
            db.session.commit()
            return redirect(url_for('home'))
    return render_template("reinitialiser_mdp.html", form=form, tentative=False, token_access=tokenObject.get_token())

def send_change_pwd_email(mail, token) -> bool:
    sent_status = False
    # email = "eexemple044@gmail.com"
    # password = "ggzb gucf uynu djih"
    email = GOOGLE_SMTP_USER
    password = GOOGLE_SMTP_PWD
    subject = "Mobilist - réinitialiser votre mot de passe"
    protocol = "http"
    domain = "127.0.0.1"
    port = "5000"
    generated_change_password_link = f"{protocol}://{domain}:{port}/forgotPassword/setPassword?token={token}"
    body = f"Pour réinitialiser votre mot de passe Mobilist,\n veuillez accéder à la page suivante : {generated_change_password_link}"
    try:
        # Configuration du serveur SMTP
        server = smtplib.SMTP(GOOGLE_SMTP)
        # server = smtplib.SMTP("smtp.gmail.com", 587) # server smtp de google
        server.starttls() 
        server.login(email, password)

        msg = MIMEMultipart()
        msg["From"] = email
        msg["To"] = mail
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server.sendmail(email, mail, msg.as_string())
        print("Email envoyé avec succès !")
        sent_status = True
    except Exception as e:
        print(f"Une erreur est survenue : {e}")
        sent_status = False 
    finally:
        server.quit()
        return sent_status
    
    
@app.route("/logement/ajout", methods =["GET","POST"])
def ajout_logement():
    if request.method == "POST":
        print("Ajout logement")
        print(f"form data: {request.form}")
        logement_name = request.form.get("name")
        logement_type = request.form.get("typeL")
        logement_address = request.form.get("address")
        logement_description = request.form.get("description")
        print(f"values: {logement_name}, {logement_type}, {logement_address}, {logement_description}")
        try: 
            proprio = Proprietaire.query.get(current_user.id_user)
            print(f"Proprio: {proprio}")

            new_logement = create_logement(logement_name, logement_type, logement_address, logement_description )

            link_logement_owner(new_logement, proprio)
            print(f"New logement: {new_logement}")

            rooms = json.loads(request.form.get("rooms-array"))
            print(f"Rooms: {rooms}")
            for room in rooms:
                print(f"setting room: {room}")
                ajout_piece_logement(new_logement, room["name"], room["description"])

            return redirect(url_for("accueil_connexion"))
        except Exception as e:
            print("Erreur lors de l'ajout du logement phase 1")
            print(e)
    return render_template("ajout_logement.html", type_logement=[type for type in LogementType])

def create_logement(name: str, type: str, address: str, description: str) -> Logement:
    session = db.session
    id_logement = Logement.next_id()
    print("id_logement:", id_logement)
    enum_type = LogementType[type]
    print("enum_type:", enum_type)
    new_logement = Logement(
        id_logement = id_logement,
        nom_logement = name,
        type_logement = enum_type,
        adresse_logement = address,
        desc_logement = description 
    )
    try:
        session.add(new_logement)
        session.commit()
        new_logement = Logement.query.get(id_logement)  
        print("Logement ajouté")
    except Exception as e:
        session.rollback()
        print("Erreur lors de l'ajout du logement phase 2")
        print(e)
    return new_logement

def ajout_piece_logement(Logement: Logement, room_name: str = "", desc: str = ""):
    session = db.session
    success = False
    try:
        id_piece = Piece.next_id()
        print(f"new piece id: {id_piece}")
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
        link = AVOIR(
            id_proprio=proprio.get_id_proprio(),
            id_logement=logement.get_id_logement()
        )
        session.add(link)
        session.commit()
        print("Logement lié au propriétaire")
        success = True
    except Exception as e:
        session.rollback()
        print("Erreur lors de la liaison du logement au propriétaire")
        print(e)
    return success


@app.route("/test/")
def test():
    return render_template_string(str(Logement.next_id()))

def extraire_informations(texte):
    doc = nlp(texte)
    donnees = {
        "prix": "",
        "date_achat": ""
    }
    for ent in doc.ents:
        if ent.label_ == "PRIX":
            donnees["prix"] = ent.text
        elif ent.label_ == "DATE":
            donnees["date_achat"] = ent.text
    return donnees

@app.route("/modifierbien/", methods=["POST", "GET"])
def modifier_bien():
    id = request.values.get("id")
    bien = Bien.get_data_bien(id)
    form_bien = AjoutBienForm()

    if request.method == "GET":
        form_bien.set_id(id)
        form_bien.prix_bien.data = bien.prix
        form_bien.nom_bien.data = bien.nom_bien
        form_bien.logement.data = form_bien.get_log_choices(bien.get_typelogement(bien).nom_logement)
        form_bien.categorie_bien.data = form_bien.get_cat_bien_choices(bien.get_catbien(bien).nom_cat)
        form_bien.type_bien.data = form_bien.get_type_bien_choices(bien.get_typebien(bien).nom_type)
        
    if request.method == "POST" and form_bien.validate_on_submit():
        try:
            nom = request.form.get("nom_bien")
            logement = request.form.get("logement")
            prix = request.form.get("prix_bien")
            date = request.form.get("date_bien")
            categorie = request.form.get("categorie_bien")
            type_b = request.form.get("type_bien")
            Bien.modifier_bien(
                int(id), 
                nom,
                int(logement),
                float(prix),
                date, 
                int(categorie), 
                int(type_b)
                ) 
            return redirect(url_for("accueil_connexion"))
        except Exception as e:
            print(e)
            return render_template("modification_bien.html", 
                               form=form_bien,     
                               error=True)
    return render_template("modification_bien.html", 
                            form=form_bien, 
                            error=False)
    