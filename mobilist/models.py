from sqlalchemy.orm import registry, relationship, Session
from sqlalchemy import select, Column, Integer, String, Enum, Date, DECIMAL, Float, String, create_engine
from .app import db, login_manager
from sqlalchemy.sql.schema import ForeignKey
from datetime import date
from flask_login import UserMixin
from sqlalchemy.sql.expression import func
import enum
import yaml, os.path
import time

Base = db.Model

class LogementType(enum.Enum):
    __tablename__ = "LOGEMENTTYPE"
    
    APPART = "appart"
    MAISON = "maison"

    def get_type(self):
        return self.name

class Avis(Base):
    __tablename__ = "AVIS"
    
    id_avis = Column(Integer, name="ID_AVIS", primary_key=True)
    desc_avis = Column(String(1000), name="DESCRIPTION", nullable=True)
    id_proprio = Column(Integer, ForeignKey("PROPRIETAIRE.ID_PROPRIO"), nullable=False, name="ID_PROPRIO")
    
    def __init__(self, id_avis, desc_avis, id_proprio):
        self.id_avis = id_avis
        self.desc_avis = desc_avis
        self.id_proprio = id_proprio
    
    def __repr__(self):
        return "<Avis (%d) %s>" % (self.id_avis, self.desc_avis)
    
    def get_id_avis(self):
        return self.id_avis
    
    def set_id_avis(self, id_avis):
        self.id_avis = id_avis
    
    def get_desc_avis(self):
        return self.desc_avis
    
    def set_desc_avis(self, desc_avis):
        self.desc_avis = desc_avis
    
    def get_id_proprio(self):
        return self.id_proprio
    
    def set_id_proprio(self, id_proprio):
        self.id_proprio = id_proprio
    
    def get_sample():
        return Avis.query.all()

class Proprietaire(Base):
    __tablename__ = "PROPRIETAIRE"
    
    id_proprio = Column(Integer, primary_key=True, name="ID_PROPRIO")
    nom = Column(String(20), name="NOM")
    prenom = Column(String(20), name="PRENOM")
    mail = Column(String(50), name="MAIL", unique=True, nullable=False)
    logements = relationship("Logement", secondary="AVOIR", back_populates="proprietaires")
    user = relationship("User", back_populates="proprio", uselist=False)
    
    def __init__(self, id_proprio, mail , nom_proprio=None, prenom_proprio=None):
        self.id_proprio = id_proprio
        self.nom = nom_proprio
        self.prenom = prenom_proprio
        self.mail = mail
    
    def __repr__(self):
        return "<Proprietaire (%d) %s %s>" % (self.id_proprio, self.nom, self.prenom)
    
    def get_id_proprio(self):
        return self.id_proprio
    
    def set_id_proprio(self, id_proprio):
        self.id_proprio = id_proprio
    
    def get_nom(self):
        return self.nom
    
    def set_nom(self, nom):
        self.nom = nom
    
    def get_prenom(self):
        return self.prenom
    
    def set_prenom(self, prenom):
        self.prenom = prenom
    
    @staticmethod
    def max_id():
        return db.session.query(func.max(Proprietaire.id_proprio)).scalar()
    
    @staticmethod
    def get_by_mail(mail):
        return Proprietaire.query.filter_by(mail=mail).first()
   
class Logement(Base):
    __tablename__ = "LOGEMENT"
    
    id_logement = Column(Integer, name="ID_LOGEMENT", primary_key=True)
    nom_logement = Column(String(20), name="NOM_LOGEMENT", nullable=True)
    type_logement = Column(Enum(LogementType), name="TYPE_LOGEMENT", nullable=False)
    adresse = Column(String(100), name="ADRESSE", nullable=True)
    desc_logement = Column(String(1000), name="DESC_LOGEMENT", nullable=True)
    proprietaires = relationship("Proprietaire", secondary="AVOIR", back_populates="logements")
    
    def __init__(self, id_logement, nom_logement,type_logement, adresse_logement, desc_logement):
        self.id_logement = id_logement
        self.nom_logement = nom_logement
        self.type_logement = type_logement
        self.adresse = adresse_logement
        self.desc_logement = desc_logement
        
    def __repr__(self):
        return "<Logement (%d) %s %s>" % (self.id_logement, self.type_logement, self.adresse)
    
    def get_id_logement(self):
        return self.id_logement
    
    def get_type_logement(self):
        return self.type_logement
    
    def get_adresse(self):
        return self.adresse
    
    def get_desc_logement(self):
        return self.desc_logement
    
    def set_id_logement(self, id_logement):
        self.id_logement = id_logement
    
    def set_type_logement(self, type_logement):
        self.type_logement = type_logement
    
    def set_adresse(self, adresse):
        self.adresse = adresse
    
    def set_desc_logement(self, desc_logement):
        self.desc_logement = desc_logement
    
class AVOIR(Base):
    __tablename__ = "AVOIR"

    id_proprio = Column(Integer, ForeignKey("PROPRIETAIRE.ID_PROPRIO"), name="ID_PROPRIO", primary_key=True)
    id_logement = Column(Integer, ForeignKey("LOGEMENT.ID_LOGEMENT"), name="ID_LOGEMENT", primary_key=True)

    def __init__(self, id_proprio, id_logement):
        self.id_proprio = id_proprio
        self.id_logement = id_logement

    def __repr__(self):
        return "Avoir %d %d" % (self.id_proprio, self.id_logement)
    
    def get_id_proprio(self):
        return self.id_proprio
    
    def set_id_proprio(self, id_proprio):
        self.id_proprio = id_proprio
    
    def get_id_logement(self):
        return self.id_logement
    
    def set_id_logement(self, id_logement):
        self.id_logement = id_logement

class Bien(Base):
    __tablename__ = "BIEN"
    
    id_bien = Column(Integer, name="ID_BIEN", primary_key=True)
    nom_bien = Column(String(100), name="NOM_BIEN", nullable=False)
    date_achat = Column(Date, name="DATE_ACHAT", nullable=True)
    prix = Column(Float, name="PRIX", nullable=True)
    id_proprio = Column(Integer, ForeignKey("PROPRIETAIRE.ID_PROPRIO"), nullable=False, name="ID_PROPRIO")
    id_piece = Column(Integer, ForeignKey("PIECE.ID_PIECE"), nullable=False, name="ID_PIECE")
    id_logement = Column(Integer, ForeignKey("PIECE.ID_LOGEMENT"), nullable=False, name="ID_LOGEMENT")
    id_type = Column(Integer, ForeignKey("TYPEBIEN.ID_TYPE_BIEN"), nullable=False, name="ID_TYPE_BIEN")
    id_cat = Column(Integer, ForeignKey("CATEGORIE.ID_CATEGORIE"), nullable=False, name="ID_CATEGORIE")
    
    
    def __init__(self, id_bien, nom_bien, id_proprio, date_achat, prix, id_piece, id_logement,  id_type, id_cat):
        self.id_bien = id_bien
        self.nom_bien = nom_bien
        self.date_achat = date_achat
        self.prix = prix
        self.id_proprio = id_proprio
        self.id_piece = id_piece
        self.id_logement = id_logement
        self.id_type = id_type
        self.id_cat = id_cat
    
    def __repr__(self):
        return "<Bien (%d) %s>" % (self.id_bien, self.nom_bien)
    
    def get_id_bien(self):
        return self.id_bien
    
    def set_id_bien(self, id_bien):
        self.id_bien = id_bien
    
    def get_nom_bien(self):
        return self.nom_bien
    
    def set_nom_bien(self, nom_bien):
        self.nom_bien = nom_bien
    
    def get_date_achat(self):
        return self.date_achat
    
    def set_date_achat(self, date_achat):
        self.date_achat = date_achat
    
    def get_prix(self):
        return self.prix
    
    def set_prix(self, prix):
        self.prix = prix
    
    def get_id_proprio(self):
        return self.id_proprio
    
    def set_id_proprio(self, id_proprio):
        self.id_proprio = id_proprio
    
    def get_id_piece(self):
        return self.id_piece
    
    def set_id_piece(self, id_piece):
        self.id_piece = id_piece
    
    def get_id_type(self):
        return self.id_type
    
    def set_id_type(self, id_type):
        self.id_type = id_type
    
    def get_id_cat(self):
        return self.id_cat
    
    def set_id_cat(self, id_cat):
        self.id_cat = id_cat

    def get_id_logement(self):
        return self.id_logement

    def set_id_logement(self, id_logement):
        self.id_logement = id_logement

    @staticmethod
    def get_max_id() -> int:
        return db.session.query(func.max(Bien.id_bien)).scalar()
    
class Piece(Base):
    __tablename__ = "PIECE"
    
    id_piece = Column(Integer, primary_key=True, nullable=False, name="ID_PIECE")
    nom_piece = Column(String(20), nullable=True, name="NOM_PIECE")
    desc_piece = Column(String(1000), nullable=True, name="DESCRIPTION")
    id_logement = Column(Integer, ForeignKey("LOGEMENT.ID_LOGEMENT"), primary_key=True, nullable=False, name="ID_LOGEMENT")
    
    def __init__(self, id_piece, nom_piece, desc_piece, id_logement):
        self.id_piece = id_piece
        self.nom_piece = nom_piece
        self.desc_piece = desc_piece
        self.id_logement = id_logement
        
    def __repr__(self):
        return "<Piece (%d) %s >" % (self.id_piece, self.nom_piece)
    
    def get_id_piece(self):
        return self.id_piece
    
    def set_id_piece(self, id_piece):
        self.id_piece = id_piece
    
    def get_nom_piece(self):
        return self.nom_piece
    
    def set_nom_piece(self, nom_piece):
        self.nom_piece = nom_piece
    
    def get_desc_piece(self):
        return self.desc_piece
    
    def set_desc_piece(self, desc_piece):
        self.desc_piece = desc_piece
    
    def get_id_logement(self):
        return self.id_logement
    
    def set_id_logement(self, id_logement):
        self.id_logement = id_logement

class TypeBien(Base):
    __tablename__ = "TYPEBIEN"
    
    id_type = Column(Integer, primary_key=True, nullable=False, name="ID_TYPE_BIEN")
    nom_type = Column(String(20), nullable=False, name="NOM_TYPE")
    
    def __init__(self, id_type, nom_type):
        self.id_type = id_type
        self.nom_type = nom_type
    
    def __repr__(self):
        return "<TypeBien (%d) %s >" % (self.id_type, self.nom_type)
    
    def get_id_type(self):
        return self.id_type
    
    def set_id_type(self, id_type):
        self.id_type = id_type
    
    def get_nom_type(self):
        return self.nom_type
    
    def set_nom_type(self, nom_type):
        self.nom_type = nom_type

class Categorie(Base):
    __tablename__ = "CATEGORIE"
    
    id_cat = Column(Integer, primary_key=True, nullable=False, name="ID_CATEGORIE")
    nom_cat = Column(String(20), nullable=False, name="NOM_CATEGORIE")
    
    def __init__(self, id_cat, nom_cat):
        self.id_cat = id_cat
        self.nom_cat = nom_cat
    
    def __repr__(self):
        return "<Categorie (%d) %s >" % (self.id_cat, self.nom_cat)
    
    def get_id_cat(self):
        return self.id_cat
    
    def set_id_cat(self, id_cat):
        self.id_cat = id_cat
    
    def get_nom_cat(self):
        return self.nom_cat
    
    def set_nom_cat(self, nom_cat):
        self.nom_cat = nom_cat

class Justificatif(Base):
    __tablename__ = "JUSTIFICATIF"
    
    id_justif = Column(Integer, primary_key=True, name="ID_JUSTIFICATIF")
    nom_justif = Column(String(30), name="NOM_JUSTIFICATIF")
    date_ajout = Column(Date, name="DATE_AJOUT")
    URL = Column(String(200), name="URL")
    id_bien = Column(Integer, ForeignKey("BIEN.ID_BIEN"), primary_key=True, name="ID_BIEN")
    
    def __init__(self, id_justif, nom_justif, date_ajout, URL, id_bien):
        self.id_justif = id_justif
        self.nom_justif = nom_justif
        self.date_ajout = date_ajout
        self.URL = URL
        self.id_bien = id_bien
    
    def __repr__(self):
        return "<Justificatif (%d) %s %s %s %d>" % (self.id_justif, self.nom_justif, self.date_ajout, self.URL, self.id_bien)
    
    def get_id_justif(self):
        return self.id_justif
    
    def set_id_justif(self, id_justif):
        self.id_justif = id_justif
    
    def get_nom_justif(self):
        return self.nom_justif
    
    def set_nom_justif(self, nom_justif):
        self.nom_justif = nom_justif
    
    def get_date_ajout(self):
        return self.date_ajout
    
    def set_date_ajout(self, date_ajout):
        self.date_ajout = date_ajout
    
    def get_URL(self):
        return self.URL
    
    def set_URL(self, URL):
        self.URL = URL
    
    def get_id_bien(self):
        return self.id_bien
    
    def set_id_bien(self, id_bien):
        self.id_bien = id_bien

class User(Base, UserMixin):
    __tablename__ = "USER"
    
    mail = Column(String(50), primary_key=True, name="MAIL")
    password = Column(String(64), name="PASSWORD")
    role = Column(String(10), name="ROLE")
    id_user = Column(Integer, ForeignKey("PROPRIETAIRE.ID_PROPRIO"), name="ID_PROPRIO")
    proprio = relationship('Proprietaire', back_populates='user', uselist=False)
    
    def get_id(self):
        return self.mail
    
    def set_id(self, mail):
        self.mail = mail
    
    def get_password(self):
        return self.password
    
    def set_password(self, password):
        self.password = password
    
    def get_role(self):
        return self.role
    
    def set_role(self, role):
        self.role = role
    
    def get_id_user(self):
        return self.id_user
    
    def set_id_user(self, id_user):
        self.id_user = id_user

    @staticmethod
    def modifier(mail, nom, prenom):
        proprio = Proprietaire.get_by_mail(mail)
        proprio.set_nom(nom)
        proprio.set_prenom(prenom)
        db.session.commit()

    @staticmethod
    def get_user(mail):
        return User.query.get_or_404(mail)
    
    @staticmethod
    def get_by_mail(mail):
        return User.query.filter_by(mail=mail).first()
    
@login_manager.user_loader
def load_user(mail):
    return User.query.get(mail)

    
