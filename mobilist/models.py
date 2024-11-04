from sqlalchemy.orm import registry, relationship, Session
from sqlalchemy import select, Column, Integer, String, Enum, Date, DECIMAL, Float, String, create_engine
from .app import db
from sqlalchemy.sql.schema import ForeignKey
from datetime import date
import yaml, os.path
import time
from flask_login import UserMixin
from sqlalchemy.sql.expression import func
import enum

# mapper_registry = registry()
Base = db.Model

class LogementType(enum.Enum):
    __tablename__ = "LOGEMENTTYPE"
    
    APPART = "appart"
    MAISON = "maison"

class Avis(Base) :
    __tablename__ = "AVIS"
    
    idAvis = Column(Integer, primary_key = True)
    descriptionAvis = Column(String(1000), nullable=False) 
    idProprio = Column(Integer, ForeignKey("PROPRIETAIRE.idProprio"), nullable=False)
    def __repr__(self):
        return "<Avis (%d) %s>" % (self.idAvis, self.descriptionAvis)
    
class Proprietaire(Base):
    __tablename__ = "PROPRIETAIRE"
    
    idProprio = Column(Integer, primary_key = True)
    nom = Column(String(20))
    prenom = Column(String(20))
    logements = relationship("Logement", secondary="AVOIR", back_populates="proprietaires")
    user = relationship("User", back_populates="id")
    
    def __repr__(self):
        return "<Proprietaire (%d) %s %s>" % (self.idProprio, self.nomProprio, self.prenom)


    
class Logement(Base):
    __tablename__ = "LOGEMENT"
    
    idLogement = Column(Integer, primary_key = True, nullable=False)
    typeL = Column(Enum(LogementType), nullable=False)
    adresse = Column(String(100))
    descriptionLogement = Column(String(1000), nullable=True)
    proprietaires = relationship("Proprietaire", secondary="AVOIR", back_populates="logements")
    def __repr__(self):
        return "<Logement (%d) %s %s>" % (self.idLogement, self.typeL, self.adresse)
    
class AVOIR(Base):
    __tablename__ = "AVOIR"

    idProprio = Column(Integer, ForeignKey("PROPRIETAIRE.idProprio"), primary_key = True)
    idLogement = Column(Integer, ForeignKey("LOGEMENT.idLogement"), primary_key = True)

    def __init__(self, idP, idL):
        self.idProprio = idP
        self.idLogement = idL

    def __repr__(self):
        return "Avoir %d %d" % (self.idProprio, self.idLogement)
    
class Bien(Base):
    __tablename__ = "BIEN"
    
    idBien = Column(Integer, primary_key = True)
    nomB = Column(String(100), nullable=False)
    dateAchat = Column(Date)
    prix = Column(Float, nullable=True)
    # idProprio = Column(Integer, ForeignKey("PROPRIETAIRE.idProprio"), nullable=False )
    idPiece = Column(Integer, ForeignKey("PIECE.idPiece"), nullable=False)
    idType = Column(Integer, ForeignKey("TYPEBIEN.idType"), nullable=False)
    idCat = Column(Integer, ForeignKey("CATEGORIE.idCat"), nullable=False)
    def __repr__(self):
        return "<Bien (%d) %s>" % (self.idBien, self.nomB)
    
class Piece(Base):
    __tablename__ = "PIECE"
    
    idPiece = Column(Integer, primary_key = True, nullable=False)
    nomPiece = Column(String(20), nullable=False)
    descriptionPiece = Column(String(1000), nullable=True)
    idLogement = Column(Integer, ForeignKey("LOGEMENT.idLogement"),  primary_key = True)

    def __repr__(self):
        return "<Piece (%d) %s >" % (self.idPiece, self.nomPiece)
    
class TypeBien(Base):
    __tablename__ = "TYPEBIEN"
    
    idType = Column(Integer, primary_key = True, nullable=False)
    nomType = Column(String(20), nullable=False)
    def __repr__(self):
        return "<TypeBien (%d) %s >" % (self.idType, self.nomType)
    
class Categorie(Base):
    __tablename__ = "CATEGORIE"
    
    idCat = Column(Integer, primary_key = True, nullable=False)
    nomCat = Column(String(20), nullable=False)
    def __repr__(self):
        return "<Categorie (%d) %s >" % (self.idCat, self.nomCat)
    
class Justificatif(Base):
    __tablename__ = "JUSTIFICATIF"
    
    idJustif = Column(Integer, primary_key = True)
    nomJustif = Column(String(30))
    dateAjout = Column(Date)
    URL = Column(String(200))
    idBien = Column(Integer, ForeignKey("BIEN.idBien"), primary_key = True)
    def __repr__(self):
        return "<Justificatif (%d) %s %s %s %d>" % (self.idJustif, self.nomJustif, self.dateAjout, self.URL, self.idBien)
    


class User(Base, UserMixin):
    __tablename__="USER"
    
    mail = Column(String(50), primary_key=True)
    password = Column(String(64))
    role = Column(String(10))
    id_user = Column(Integer, ForeignKey("PROPRIETAIRE.idProprio"))
    id = relationship('Proprietaire', back_populates='user')
    
    def get_id(self):
        return self.mail
    
def get_user(mail):
    return User.query.get_or_404(mail)

def get_proprio(id):
    return Proprietaire.query.get_or_404(id)
    

from .app import login_manager
@login_manager.user_loader
def load_user(mail):
    return User.query.get(mail)

def max_id():
    return db.session.query(func.max(Proprietaire.idProprio)).scalar()