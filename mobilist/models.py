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

    def get_type(self) -> str:
        return self.name

class Avis(Base):
    __tablename__ = "AVIS"
    
    id_avis = Column(Integer, name="ID_AVIS", primary_key=True)
    desc_avis = Column(String(1000), name="DESCRIPTION", nullable=True)
    id_proprio = Column(Integer, ForeignKey("PROPRIETAIRE.ID_PROPRIO"), nullable=False, name="ID_PROPRIO")
    
    def __init__(self, id_avis: int, desc_avis: str, id_proprio: int) -> None:
        self.id_avis = id_avis
        self.desc_avis = desc_avis
        self.id_proprio = id_proprio
    
    def __repr__(self) -> str:
        return "<Avis (%d) %s>" % (self.id_avis, self.desc_avis)
    
    def get_id_avis(self) -> int:
        return self.id_avis
    
    def set_id_avis(self, id_avis: int) -> None:
        self.id_avis = id_avis
    
    def get_desc_avis(self) -> str:
        return self.desc_avis
    
    def set_desc_avis(self, desc_avis: str) -> None:
        self.desc_avis = desc_avis
    
    def get_id_proprio(self) -> int:
        return self.id_proprio
    
    def set_id_proprio(self, id_proprio: int) -> None:
        self.id_proprio = id_proprio
    
    def get_sample():
        return Avis.query.all()

    @staticmethod
    def get_sample() -> list["Avis"]:
        return Avis.query.all()

class Proprietaire(Base):
    __tablename__ = "PROPRIETAIRE"
    
    id_proprio = Column(Integer, primary_key=True, name="ID_PROPRIO")
    nom = Column(String(20), name="NOM")
    prenom = Column(String(20), name="PRENOM")
    mail = Column(String(50), name="MAIL", unique=True, nullable=False)
    logements = relationship("Logement", secondary="AVOIR", back_populates="proprietaires")
    user = relationship("User", back_populates="proprio", uselist=False)
    
    def __init__(self, id_proprio: int, mail: str, nom_proprio: str = None, prenom_proprio: str = None) -> None:
        self.id_proprio = id_proprio
        self.nom = nom_proprio
        self.prenom = prenom_proprio
        self.mail = mail
    
    def __repr__(self) -> str:
        return "<Proprietaire (%d) %s %s>" % (self.id_proprio, self.nom, self.prenom)
    
    def get_id_proprio(self) -> int:
        return self.id_proprio
    
    def set_id_proprio(self, id_proprio: int) -> None:
        self.id_proprio = id_proprio
    
    def get_nom(self) -> str:
        return self.nom
    
    def set_nom(self, nom: str) -> None:
        self.nom = nom
    
    def get_prenom(self) -> str:
        return self.prenom
    
    def set_prenom(self, prenom: str) -> None:
        self.prenom = prenom
    
    @staticmethod
    def max_id() -> int:
        return db.session.query(func.max(Proprietaire.id_proprio)).scalar()
    
    @staticmethod
    def get_by_mail(mail: str) -> "Proprietaire":
        return Proprietaire.query.filter_by(mail=mail).first()
  
class Logement(Base):
    __tablename__ = "LOGEMENT"
    
    id_logement = Column(Integer, name="ID_LOGEMENT", primary_key=True)
    nom_logement = Column(String(20), name="NOM_LOGEMENT", nullable=True)
    type_logement = Column(Enum(LogementType), name="TYPE_LOGEMENT", nullable=False)
    adresse = Column(String(100), name="ADRESSE", nullable=True)
    desc_logement = Column(String(1000), name="DESC_LOGEMENT", nullable=True)
    proprietaires = relationship("Proprietaire", secondary="AVOIR", back_populates="logements")
    
    def __init__(self, id_logement: int, nom_logement: str, type_logement: LogementType, adresse_logement: str, desc_logement: str) -> None:
        self.id_logement = id_logement
        self.nom_logement = nom_logement
        self.type_logement = type_logement
        self.adresse = adresse_logement
        self.desc_logement = desc_logement
        
    def __repr__(self) -> str:
        return "<Logement (%d) %s %s>" % (self.id_logement, self.type_logement, self.adresse)
    
    def get_id_logement(self) -> int:
        return self.id_logement
    
    def get_type_logement(self) -> LogementType:
        return self.type_logement
    
    def get_nom_logement(self) -> str:
        return self.nom_logement
    
    def set_nom_logement(self, nom_logement: str) -> None:
        self.nom_logement = nom_logement
    
    def get_adresse(self) -> str:
        return self.adresse
    
    def get_desc_logement(self) -> str:
        return self.desc_logement
    
    def get_nom_logement(self):
        return self.nom_logement
    
    def set_id_logement(self, id_logement: str) -> None:
        self.id_logement = id_logement
    
    def set_type_logement(self, type_logement: LogementType) -> None:
        self.type_logement = type_logement
    
    def set_adresse(self, adresse: str) -> None:
        self.adresse = adresse
    
    def set_desc_logement(self, desc_logement: str) -> None:
        self.desc_logement = desc_logement

    def set_nom_logement(self, nom_logement):
        self.nom_logement = nom_logement

    def get_pieces_list(self) -> list:
        return Piece.query.filter_by(id_logement=self.id_logement).all()

    
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
from datetime import date
from flask_login import UserMixin
import time

class AVOIR(Base):
    __tablename__ = "AVOIR"

    id_proprio = Column(Integer, ForeignKey("PROPRIETAIRE.ID_PROPRIO"), name="ID_PROPRIO", primary_key=True)
    id_logement = Column(Integer, ForeignKey("LOGEMENT.ID_LOGEMENT"), name="ID_LOGEMENT", primary_key=True)

    def __init__(self, id_proprio: int, id_logement: int) -> None:
        self.id_proprio = id_proprio
        self.id_logement = id_logement

    def __repr__(self) -> str:
        return "Avoir %d %d" % (self.id_proprio, self.id_logement)
    
    def get_id_proprio(self) -> int:
        return self.id_proprio
    
    def set_id_proprio(self, id_proprio: int) -> None:
        self.id_proprio = id_proprio
    
    def get_id_logement(self) -> int:
        return self.id_logement
    
    def set_id_logement(self, id_logement: int) -> None:
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
    
    def __init__(self, id_bien: int, nom_bien: str, id_proprio: int, date_achat: date, prix: float,
                 id_piece: int, id_logement: int, id_type: int, id_cat: int) -> None:
        self.id_bien = id_bien
        self.nom_bien = nom_bien
        self.date_achat = date_achat
        self.prix = prix
        self.id_proprio = id_proprio
        self.id_piece = id_piece
        self.id_logement = id_logement
        self.id_type = id_type
        self.id_cat = id_cat
    
    def __repr__(self) -> str:
        return "<Bien (%d) %s>" % (self.id_bien, self.nom_bien)
    
    def get_id_bien(self) -> int:
        return self.id_bien
    
    def set_id_bien(self, id_bien: int) -> None:
        self.id_bien = id_bien
    
    def get_nom_bien(self) -> str:
        return self.nom_bien
    
    def set_nom_bien(self, nom_bien: str) -> None:
        self.nom_bien = nom_bien
    
    def get_date_achat(self) -> date:
        return self.date_achat
    
    def set_date_achat(self, date_achat: str) -> None:
        date_format = '%Y-%m-%d'
        self.date_achat = time.strptime(date_achat, date_format)
    
    def get_prix(self) -> float:
        return self.prix
    
    def set_prix(self, prix: float) -> None:
        self.prix = prix
    
    def get_id_proprio(self) -> int:
        return self.id_proprio
    
    def set_id_proprio(self, id_proprio: int) -> None:
        self.id_proprio = id_proprio
    
    def get_id_piece(self) -> int:
        return self.id_piece
    
    def set_id_piece(self, id_piece: int) -> None:
        self.id_piece = id_piece
    
    def get_id_type(self) -> int:
        return self.id_type
    
    def set_id_type(self, id_type: int) -> None:
        self.id_type = id_type
    
    def get_id_cat(self) -> int:
        return self.id_cat
    
    def set_id_cat(self, id_cat: int) -> None:
        self.id_cat = id_cat

    def get_id_logement(self) -> int:
        return self.id_logement

    def set_id_logement(self, id_logement: int) -> None:
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
    
    def __init__(self, id_piece: int, nom_piece: str, desc_piece: str, id_logement: int) -> None:
        self.id_piece = id_piece
        self.nom_piece = nom_piece
        self.desc_piece = desc_piece
        self.id_logement = id_logement
        
    def __repr__(self) -> str:
        return "<Piece (%d) %s >" % (self.id_piece, self.nom_piece)
    
    def get_id_piece(self) -> int:
        return self.id_piece
    
    def set_id_piece(self, id_piece: int) -> None:
        self.id_piece = id_piece
    
    def get_nom_piece(self) -> str:
        return self.nom_piece
    
    def set_nom_piece(self, nom_piece: str) -> None:
        self.nom_piece = nom_piece
    
    def get_desc_piece(self) -> str:
        return self.desc_piece
    
    def set_desc_piece(self, desc_piece: str) -> None:
        self.desc_piece = desc_piece
    
    def get_id_logement(self) -> int:
        return self.id_logement
    
    def set_id_logement(self, id_logement: int) -> None:
        self.id_logement = id_logement

    def get_list_biens(self):
        return Bien.query.filter_by(id_logement=self.id_logement,id_piece=self.id_piece).all()
        

class TypeBien(Base):
    __tablename__ = "TYPEBIEN"
    
    id_type = Column(Integer, primary_key=True, nullable=False, name="ID_TYPE_BIEN")
    nom_type = Column(String(20), nullable=False, name="NOM_TYPE")
    
    def __init__(self, id_type: int, nom_type: str) -> None:
        self.id_type = id_type
        self.nom_type = nom_type
    
    def __repr__(self) -> str:
        return "<TypeBien (%d) %s >" % (self.id_type, self.nom_type)
    
    def get_id_type(self) -> int:
        return self.id_type
    
    def set_id_type(self, id_type: int) -> None:
        self.id_type = id_type
    
    def get_nom_type(self) -> str:
        return self.nom_type
    
    def set_nom_type(self, nom_type: str) -> None:
        self.nom_type = nom_type

class Categorie(Base):
    __tablename__ = "CATEGORIE"
    
    id_cat = Column(Integer, primary_key=True, nullable=False, name="ID_CATEGORIE")
    nom_cat = Column(String(20), nullable=False, name="NOM_CATEGORIE")
    
    def __init__(self, id_cat: int, nom_cat: str) -> None:
        self.id_cat = id_cat
        self.nom_cat = nom_cat
    
    def __repr__(self) -> str:
        return "<Categorie (%d) %s >" % (self.id_cat, self.nom_cat)
    
    def get_id_cat(self) -> int:
        return self.id_cat
    
    def set_id_cat(self, id_cat: int) -> None:
        self.id_cat = id_cat
    
    def get_nom_cat(self) -> str:
        return self.nom_cat
    
    def set_nom_cat(self, nom_cat: str) -> None:
        self.nom_cat = nom_cat

class Justificatif(Base):
    __tablename__ = "JUSTIFICATIF"
    
    id_justif = Column(Integer, primary_key=True, name="ID_JUSTIFICATIF")
    nom_justif = Column(String(30), name="NOM_JUSTIFICATIF")
    date_ajout = Column(Date, name="DATE_AJOUT")
    URL = Column(String(200), name="URL")
    id_bien = Column(Integer, ForeignKey("BIEN.ID_BIEN"), primary_key=True, name="ID_BIEN")
    
    def __init__(self, id_justif: int, nom_justif: str, date_ajout: date, URL: str, id_bien: int) -> None:
        self.id_justif = id_justif
        self.nom_justif = nom_justif
        self.date_ajout = date_ajout
        self.URL = URL
        self.id_bien = id_bien
    
    def __repr__(self) -> str:
        return "<Justificatif (%d) %s %s %s %d>" % (self.id_justif, self.nom_justif, self.date_ajout, self.URL, self.id_bien)
    
    def get_id_justif(self) -> int:
        return self.id_justif
    
    def set_id_justif(self, id_justif: int) -> None:
        self.id_justif = id_justif
    
    def get_nom_justif(self) -> str:
        return self.nom_justif
    
    def set_nom_justif(self, nom_justif: str) -> None:
        self.nom_justif = nom_justif
    
    def get_date_ajout(self) -> date:
        return self.date_ajout
    
    def set_date_ajout(self, date_ajout: date) -> None:
        self.date_ajout = date_ajout
    
    def get_URL(self) -> str:
        return self.URL
    
    def set_URL(self, URL: str) -> None:
        self.URL = URL
    
    def get_id_bien(self) -> int:
        return self.id_bien
    
    def set_id_bien(self, id_bien: int) -> None:
        self.id_bien = id_bien

class User(Base, UserMixin):
    __tablename__ = "USER"
    
    mail = Column(String(50), primary_key=True, name="MAIL")
    password = Column(String(64), name="PASSWORD")
    role = Column(String(10), name="ROLE")
    id_user = Column(Integer, ForeignKey("PROPRIETAIRE.ID_PROPRIO"), name="ID_PROPRIO")    
    proprio = relationship('Proprietaire', back_populates='user', uselist=False)
    
    def get_id(self) -> str:
        return self.mail
    
    def set_id(self, mail: str) -> None:
        self.mail = mail
    
    def get_password(self) -> str:
        return self.password
    
    def set_password(self, password: str) -> None:
        self.password = password
    
    def get_role(self) -> str:
        return self.role
    
    def set_role(self, role: str) -> None:
        self.role = role
    
    def get_id_user(self) -> int:
        return self.id_user
    
    def set_id_user(self, id_user: int) -> None:
        self.id_user = id_user

    @staticmethod
    def modifier(mail: str, nom: str, prenom: str) -> None:
        proprio = Proprietaire.get_by_mail(mail)
        proprio.set_nom(nom)
        proprio.set_prenom(prenom)
        db.session.commit()

    @staticmethod
    def get_user(mail: str) -> "User":
        return User.query.get_or_404(mail)
    
    @staticmethod
    def get_by_mail(mail: str) -> "User":
        return User.query.filter_by(mail=mail).first()
    
    @login_manager.user_loader
    def load_user(mail: str) -> "User":
        return User.query.get(mail)
