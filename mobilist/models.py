from sqlalchemy.orm import registry, relationship, Session
from sqlalchemy import select, Column, Integer, String, Enum, Date, DECIMAL, Float, String, create_engine
from .app import db
from sqlalchemy.sql.schema import ForeignKey
from datetime import date
import yaml, os.path
import time
import enum

# mapper_registry = registry()
Base = db.Model

class LogementType(enum.Enum):
    __tablename__ = "LOGEMENTTYPE"
    
    APPART = "appart"
    MAISON = "maison"

class Avis(Base) :
    __tablename__ = "AVIS"
    
    id_avis = Column(Integer, primary_key = True, nullable=False)
    desc_avis = Column(String(1000), nullable=False) 
    id_proprio = Column(Integer, ForeignKey("PROPRIETAIRE.id_proprio"), nullable=False)
    
    def __init__(self, id_avis, desc_avis, id_proprio):
        self.id_avis = id_avis
        self.desc_avis = desc_avis
        self.id_proprio = id_proprio
    
    def __repr__(self):
        return "<Avis (%d) %s>" % (self.id_avis, self.desc_avis)
    
class Proprietaire(Base):
    __tablename__ = "PROPRIETAIRE"
    
    id_proprio = Column(Integer, primary_key = True, nullable=False)
    nom = Column(String(20), nullable=False)
    prenom = Column(String(20), nullable=False)
    logements = relationship("Logement", secondary="AVOIR", back_populates="proprietaires")
    
    def __init__(self, id_proprio, nom_proprio, prenom_proprio):
        self.id_proprio = id_proprio
        self.nom = nom_proprio
        self.prenom = prenom_proprio
    
    def __repr__(self):
        return "<Proprietaire (%d) %s %s>" % (self.id_proprio, self.nom, self.prenom)

class Logement(Base):
    __tablename__ = "LOGEMENT"
    
    id_logement = Column(Integer, primary_key = True, nullable=False)
    type_logement = Column(Enum(LogementType), nullable=False)
    adresse = Column(String(100), nullable=True)
    desc_logement = Column(String(1000), nullable=True)
    proprietaires = relationship("Proprietaire", secondary="AVOIR", back_populates="logements")
    
    def __init__(self, id_logement, type_logement, adresse_logement, desc_logement):
        self.id_logement = id_logement
        self.type_logement = type_logement
        self.adresse = adresse_logement
        self.desc_logement = desc_logement
        
    def __repr__(self):
        return "<Logement (%d) %s %s>" % (self.id_logement, self.type_logement, self.adresse)
    
class AVOIR(Base):
    __tablename__ = "AVOIR"

    id_proprio = Column(Integer, ForeignKey("PROPRIETAIRE.id_proprio"), primary_key = True)
    id_logement = Column(Integer, ForeignKey("LOGEMENT.id_logement"), primary_key = True)

    def __init__(self, id_proprio, id_logement):
        self.id_proprio = id_proprio
        self.id_logement = id_logement

    def __repr__(self):
        return "Avoir %d %d" % (self.id_proprio, self.id_logement)
    
class Bien(Base):
    __tablename__ = "BIEN"
    
    id_bien = Column(Integer, primary_key = True, nullable=False)
    nom_bien = Column(String(100), nullable=False)
    date_achat = Column(Date, nullable=True)
    prix = Column(Float, nullable=True)
    # idProprio = Column(Integer, ForeignKey("PROPRIETAIRE.idProprio"), nullable=False )
    id_piece = Column(Integer, ForeignKey("PIECE.id_piece"), nullable=False)
    id_type = Column(Integer, ForeignKey("TYPEBIEN.id_type"), nullable=False)
    id_cat = Column(Integer, ForeignKey("CATEGORIE.id_cat"), nullable=False)
    
    def __init__(self, id_bien, nom_bien, date_achat, prix, id_piece, id_type, id_cat):
        self.id_bien = id_bien
        self.nom_bien = nom_bien
        self.date_achat = date_achat
        self.prix = prix
        self.id_piece = id_piece
        self.id_type = id_type
        self.id_cat = id_cat
    
    def __repr__(self):
        return "<Bien (%d) %s>" % (self.id_bien, self.nom_bien)
    
class Piece(Base):
    __tablename__ = "PIECE"
    
    id_piece = Column(Integer, primary_key = True, nullable=False)
    nom_piece = Column(String(20), nullable=False)
    desc_piece = Column(String(1000), nullable=True)
    id_logement = Column(Integer, ForeignKey("LOGEMENT.id_logement"),  primary_key = True)
    
    def __init__(self, id_piece, nom_piece, desc_piece, id_logement):
        self.id_piece = id_piece
        self.nom_piece = nom_piece
        self.desc_piece = desc_piece
        self.id_logement = id_logement
        
    def __repr__(self):
        return "<Piece (%d) %s >" % (self.id_piece, self.nom_piece)
    
class TypeBien(Base):
    __tablename__ = "TYPEBIEN"
    
    id_type = Column(Integer, primary_key = True, nullable=False)
    nom_type = Column(String(20), nullable=False)
    
    def __init__(self, id_type, nom_type):
        self.id_type = id_type
        self.nom_type = nom_type
    
    def __repr__(self):
        return "<TypeBien (%d) %s >" % (self.id_type, self.nom_type)
    
class Categorie(Base):
    __tablename__ = "CATEGORIE"
    
    id_cat = Column(Integer, primary_key = True, nullable=False)
    nom_cat = Column(String(20), nullable=False)
    
    def __init__(self, id_cat, nom_cat):
        self.id_cat = id_cat
        self.nom_cat = nom_cat
    
    def __repr__(self):
        return "<Categorie (%d) %s >" % (self.id_cat, self.nom_cat)
    
class Justificatif(Base):
    __tablename__ = "JUSTIFICATIF"
    
    id_justif = Column(Integer, primary_key = True)
    nom_justif = Column(String(30))
    date_ajout = Column(Date)
    URL = Column(String(200))
    id_bien = Column(Integer, ForeignKey("BIEN.id_bien"), primary_key = True)
    
    def __init__(self, id_justif, nom_justif, date_ajout, URL, id_bien):
        self.id_justif = id_justif
        self.nom_justif = nom_justif
        self.date_ajout = date_ajout
        self.URL = URL
        self.id_bien = id_bien
    
    def __repr__(self):
        return "<Justificatif (%d) %s %s %s %d>" % (self.id_justif, self.nom_justif, self.date_ajout, self.URL, self.id_bien)