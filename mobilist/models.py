import yaml, os.path
from sqlalchemy.orm import registry, relationship, Session
from sqlalchemy import select, Column, Integer, Text, Enum, Date, DECIMAL, Float, create_engine
import sqlalchemy
from sqlalchemy.sql.schema import ForeignKey
import time
from datetime import date
import enum

mapper_registry = registry()
Base = mapper_registry.generate_base()

def ouvrir_connexion(user,passwd,host,database,port=3306):
    """
    ouverture d'une connexion MySQL
    paramètres:
       user     (str) le login MySQL de l'utilsateur
       passwd   (str) le mot de passe MySQL de l'utilisateur
       host     (str) le nom ou l'adresse IP de la machine hébergeant le serveur MySQL
       database (str) le nom de la base de données à utiliser
    résultat: L'engine de la BD
    """
    try:
        #creation de l'objet gérant les interactions avec le serveur de BD
        # engine=create_engine('mysql://'+user+':'+passwd+'@'+host+':'+port+'/'+database)
        engine=create_engine(f'mysql://{user}:{passwd}@{host}:{port}/{database}')
        #creation de la connexion
        cnx = engine.connect()
    except Exception as err:
        print(err)
        raise err
    print("connexion réussie")
    return engine 

class LogementType(enum.Enum):
    __tablename__ = "LOGEMENTTYPE"
    
    APPART = "appart"
    MAISON = "maison"

class Avis(Base) :
    __tablename__ = "AVIS"
    
    idAvis = Column(Integer, primary_key = True, nullable=False)
    descriptionAvis = Column(Text(1000), nullable=False) 
    idProprio = Column(Integer, ForeignKey("PROPRIETAIRE.idProprio"), nullable=False)
    def __repr__(self):
        return "<Avis (%d) %s>" % (self.idAvis, self.descriptionAvis)
    
class Proprietaire(Base):
    __tablename__ = "PROPRIETAIRE"
    
    idProprio = Column(Integer, primary_key = True, nullable=False)
    nomProprio = Column(Text(20), nullable=False)
    prenom = Column(Text(20), nullable=False)
    logements = relationship("Logement", back_populates = "proprio")
    def __repr__(self):
        return "<Proprietaire (%d) %s %s>" % (self.idProprio, self.nomProprio, self.prenom)

class Logement(Base):
    __tablename__ = "LOGEMENT"
    
    idLogement = Column(Integer, primary_key = True, nullable=False)
    typeL = Column(Enum(LogementType), nullable=False)
    adresse = Column(Text(100), nullable=True)
    descriptionLogement = Column(Text(1000), nullable=True)
    proprio = relationship("Proprietaire" , back_populates = "logements")
    def __repr__(self):
        return "<Logement (%d) %s %s>" % (self.idLogement, self.typeL, self.adresse)
    
class Bien(Base):
    __tablename__ = "BIEN"
    
    idBien = Column(Integer, primary_key = True, nullable=False)
    nomB = Column(Text(100), nullable=False)
    dateAchat = Column(Date, nullable=True)
    prix = Column(Float, nullable=True)
    idProprio = Column(Integer, ForeignKey("PROPRIETAIRE.idProprio"), nullable=False )
    idPiece = Column(Integer, ForeignKey("PIECE.idPiece"), nullable=False)
    idType = Column(Integer, ForeignKey("TYPEBIEN.idType"), nullable=False)
    idCat = Column(Integer, ForeignKey("CATEGORIE.idCat"), nullable=False)
    def __repr__(self):
        return "<Bien (%d) %s>" % (self.idBien, self.nomB)
    
class Piece(Base):
    __tablename__ = "PIECE"
    
    idPiece = Column(Integer, primary_key = True, nullable=False)
    nomPiece = Column(Text(20), nullable=False)
    descriptionPiece = Column(Text(1000), nullable=True)
    idLogement = Column(Integer, ForeignKey("LOGEMENT.idLogement"),  primary_key = True)

    def __repr__(self):
        return "<Piece (%d) %s >" % (self.idPiece, self.nomPiece)
    
class TypeBien(Base):
    __tablename__ = "TYPEBIEN"
    
    idType = Column(Integer, primary_key = True, nullable=False)
    nomType = Column(Text(20), nullable=False)
    def __repr__(self):
        return "<TypeBien (%d) %s >" % (self.idType, self.nomType)
    
class Categorie(Base):
    __tablename__ = "CATEGORIE"
    
    idCat = Column(Integer, primary_key = True, nullable=False)
    nomCat = Column(Text(20), nullable=False)
    def __repr__(self):
        return "<Categorie (%d) %s >" % (self.idCat, self.nomCat)
    
class Justificatif(Base):
    __tablename__ = "JUSTIFICATIF"
    
    idJustif = Column(Integer, primary_key = True)
    nomJustif = Column(Text(30))
    dateAjout = Column(Date)
    URL = Column(Text(200))
    idBien = Column(Integer, ForeignKey("BIEN.idBien"), primary_key = True)
    def __repr__(self):
        return "<Justificatif (%d) %s %s %s %d>" % (self.idJustif, self.nomJustif, self.dateAjout, self.URL, self.idBien)