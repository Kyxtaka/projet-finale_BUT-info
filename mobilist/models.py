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
        """Init d'un Avis

        Args:
            id_avis (int): ID unique de l'avis
            desc_avis (str): Contenu de l'avis (nullable)
            id_proprio (int): ID unique du propriétaire ayant posté l'avis
        """
        self.id_avis = id_avis
        self.desc_avis = desc_avis
        self.id_proprio = id_proprio
    
    def __repr__(self) -> str:
        """Représentation de la classe Avis

        Returns:
            str: Chaîne de caractère contenant l'id de l'avis et sa description
        """
        return "<Avis (%d) %s>" % (self.id_avis, self.desc_avis)
    
    def get_id_avis(self) -> int:
        """Getter de l'ID de l'avis

        Returns:
            int: ID de l'avis
        """
        return self.id_avis
    
    def set_id_avis(self, id_avis: int) -> None:
        """Changer l'ID de l'avis

        Args:
            id_avis (int): Nouvelle ID pour avis (doit être unique)
        """
        self.id_avis = id_avis
    
    def get_desc_avis(self) -> str:
        """Getter de du contenu de l'avis

        Returns:
            str: Contenu de l'avis
        """
        return self.desc_avis
    
    def set_desc_avis(self, desc_avis: str) -> None:
        """Changer le contenu de l'avis

        Args:
            desc_avis (str): Nouveau contenu pour l'avis
        """
        self.desc_avis = desc_avis
    
    def get_id_proprio(self) -> int:
        """Getter de l'ID du propriétaire (ayant posté l'avis)

        Returns:
            int: ID du propriétaire
        """
        return self.id_proprio
    
    def set_id_proprio(self, id_proprio: int) -> None:
        """Changer le propriétaire ayant posté l'avis

        Args:
            id_proprio (int): Nouvelle ID pour le propriétaire
        """
        self.id_proprio = id_proprio

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
        """Init d'un propriétaire

        Args:
            id_proprio (int): ID du propriétaire (unique)
            nom_proprio (str, optional): Nom du propriétaire. Defaults to None.
            prenom_proprio (str, optional): Prénom du propriétaire. Defaults to None.
        """
        self.id_proprio = id_proprio
        self.nom = nom_proprio
        self.prenom = prenom_proprio
        self.mail = mail
    
    def __repr__(self) -> str:
        """Représentation d'un propriétaire

        Returns:
            str: Une chaîne de caractère contenant l'ID, le nom, et le prénom
        """
        return "<Proprietaire (%d) %s %s>" % (self.id_proprio, self.nom, self.prenom)
    
    def get_id_proprio(self) -> int:
        """Getter de l'ID du propriétaire

        Returns:
            int: ID du propriétaire
        """
        return self.id_proprio
    
    def set_id_proprio(self, id_proprio: int) -> None:
        """Changer l'ID du propriétaire

        Args:
            id_proprio (int): Nouvel ID (unique)
        """
        self.id_proprio = id_proprio
    
    def get_nom(self) -> str:
        """Getter du nom

        Returns:
            str: Nom du propriétaire
        """
        return self.nom
    
    def set_nom(self, nom: str) -> None:
        """Changer le nom 

        Args:
            nom (str): Nouveau nom
        """
        self.nom = nom
    
    def get_prenom(self) -> str:
        """Getter du prénom 

        Returns:
            str: Prénom du propriétaire
        """
        return self.prenom
    
    def set_prenom(self, prenom: str) -> None:
        """modificatuin du prénom du propriétaire

        Args:
            prenom (str): nouveau prénom
        """
        self.prenom = prenom
    
    @staticmethod
    def max_id() -> int:
        """fonction de recherche de l'ID max non attribué des propriétaires

        Returns:
            int: ID max
        """
        return db.session.query(func.max(Proprietaire.id_proprio)).scalar()
    
    @staticmethod
    def get_by_mail(mail: str) -> "Proprietaire":
        """Get propriétaire par son mail

        Args:
            mail (str): email du propriétaire

        Returns:
            Proprietaire: Propriétaire
        """
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
        """Init d'un logement

        Args:
            id_logement (int): ID du logement (unique)
            nom_logement (str): Nom du logement
            type_logement (enum(str)): "appart" ou "maison"
            adresse_logement (str): Adresse du logmeent 
            desc_logement (str): Description du logement 
        """
        self.id_logement = id_logement
        self.nom_logement = nom_logement
        self.type_logement = type_logement
        self.adresse = adresse_logement
        self.desc_logement = desc_logement
        
    def __repr__(self) -> str:
        """Représentation d'un logement 

        Returns:
            str: Contenant l'ID, le type, et l'adresse
        """
        return "<Logement (%d) %s %s>" % (self.id_logement, self.type_logement, self.adresse)
    
    def get_id_logement(self) -> int:
        """Getter de l'ID du logement

        Returns:
            int: ID du logement
        """
        return self.id_logement
    
    def get_type_logement(self) -> LogementType:
        """Getter du type du logement

        Returns:
            str: Type du logement 
        """
        return self.type_logement
    
    def get_nom_logement(self) -> str:
        """Getter du nom du logement

        Returns:
            str: nom du logement
        """
        return self.nom_logement
    
    def set_nom_logement(self, nom_logement: str) -> None:
        """Modifie le nom du logement

        Args:
            nom_logement (str): nouveau nom du logement
        """
        self.nom_logement = nom_logement
    
    def get_adresse(self) -> str:
        """Getter de l'adresse

        Returns:
            str: Adresse du logement
        """
        return self.adresse
    
    def get_desc_logement(self) -> str:
        """Getter de la descritpion du logement 

        Returns:
            str: Description du logement 
        """
        return self.desc_logement
    
    def set_id_logement(self, id_logement: str) -> None:
        """Changer l'id du logement 

        Args:
            id_logement (int): Nouvel id (unique)
        """
        self.id_logement = id_logement
    
    def set_type_logement(self, type_logement: LogementType) -> None:
        """Changer le type du logement 

        Args:
            type_logement (enum(str)): "maison" ou "appartement"
        """
        self.type_logement = type_logement
    
    def set_adresse(self, adresse: str) -> None:
        """Changer l'adresse du logement 

        Args:
            adresse (str): nouvelle adresse du logement 
        """
        self.adresse = adresse
    
    def set_desc_logement(self, desc_logement: str) -> None:
        """Changer la description du logement 

        Args:
            desc_logement (str): nouvelle description du logement 
        """
        self.desc_logement = desc_logement

    def get_pieces_list(self) -> list:
        """Getter de toute les pièces du logement

        Returns:
            list: Liste de pièces
        """
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
        """init d'un lien entre logement et propriétaire

        Args:
            id_proprio (int): id du propriétaire 
            id_logement (int): id du logement 
        """
        self.id_proprio = id_proprio
        self.id_logement = id_logement

    def __repr__(self) -> str:
        """représentation du lien entre propriétaire et appartement 

        Returns:
            str : une chaine ce craractère contenant l'id du propriéatire et celuo du logement
        """
        return "Avoir %d %d" % (self.id_proprio, self.id_logement)
    
    def get_id_proprio(self) -> int:
        """getter de l'ID du propriétaire

        Returns:
            int: id du propriétaire
        """
        return self.id_proprio
    
    def set_id_proprio(self, id_proprio: int) -> None:
        """changer l'id du propriétaire

        Args:
            id_proprio (int): nouvel id du propriétaire
        """
        self.id_proprio = id_proprio
    
    def get_id_logement(self) -> int:
        """getter de l'id du logement

        Returns:
            int: id du logement
        """
        return self.id_logement
    
    def set_id_logement(self, id_logement: int) -> None:
        """changer l'id du logement

        Args:
            id_proprio (int): nouvel id du logement
        """
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
        """_summary_

        Args:
            id_bien (int): id du bien (unique)
            nom_bien (str): nom du bien
            id_proprio (int): id du propriétaire du bien
            date_achat (str): date de l'achat du bien
            prix (float): prix à l'achat du bien
            id_piece (int): id de la pièece où est situé le bien
            id_type (int): 
            id_cat (int): _description_
        """
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
        """représneation d'un bien

        Returns:
            str: représentation contenant son id et son nom
        """
        return "<Bien (%d) %s>" % (self.id_bien, self.nom_bien)
    
    def get_id_bien(self) -> int:
        """getter de l'id du bien

        Returns:
            int: ID
        """
        return self.id_bien
    
    def set_id_bien(self, id_bien: int) -> None:
        """modifie l'ID du bien (unique)

        Args:
            id_bien (int): nouvel ID (unique)
        """
        self.id_bien = id_bien
    
    def get_nom_bien(self) -> str:
        """getter du nom

        Returns:
            str: nom du bien
        """
        return self.nom_bien
    
    def set_nom_bien(self, nom_bien: str) -> None:
        """modifie le nom du bien

        Args:
            nom_bien (str): nouveau nom du bien
        """
        self.nom_bien = nom_bien
    
    def get_date_achat(self) -> date:
        """getter de la date d'achat

        Returns:
            date: date d'achat
        """
        return self.date_achat
    
    def set_date_achat(self, date_achat: str) -> None:
        """modifie la date d'achat

        Args:
            date_achat (str): nouvelle date d'achat
        """
        date_format = '%Y-%m-%d'
        self.date_achat = time.strptime(date_achat, date_format)
    
    def get_prix(self) -> float:
        """getter du prix du bien à l'achat

        Returns:
            float: prix
        """
        return self.prix
    
    def set_prix(self, prix: float) -> None:
        """modifie le prix du bien à l'achat

        Args:
            prix (float): nouveau prix
        """
        self.prix = prix
    
    def get_id_proprio(self) -> int:
        """getter de l'ID du proprio

        Returns:
            int: id du proprio
        """ 
        return self.id_proprio
    
    def set_id_proprio(self, id_proprio: int) -> None:
        """modifie l'id du proprio

        Args:
            id_proprio (int): nouvel id 
        """
        self.id_proprio = id_proprio
    
    def get_id_piece(self) -> int:
        """getter de l'id de la pièce

        Returns:
            int: id de la pièce
        """
        return self.id_piece
    
    def set_id_piece(self, id_piece: int) -> None:
        """modifie l'id de la piece

        Args:
            id_piece (int): nouvel id 
        """
        self.id_piece = id_piece
    
    def get_id_type(self) -> int:
        """getter de l'id du type du bien

        Returns:
            int: id du type de bien
        """
        return self.id_type
    
    def set_id_type(self, id_type: int) -> None:
        """modifie l'id du type de bien

        Args:
            id_type (int): nouvel id du type de bien
        """     
        self.id_type = id_type
    
    def get_id_cat(self) -> int:
        """getter de l'id de la catégorie du bien       

        Returns:
            int: id de la catégorie
        """
        return self.id_cat
    
    def set_id_cat(self, id_cat: int) -> None:
        """modifie l'id de la categorie du bien

        Args:
            id_cat (int): nouvel id
        """
        self.id_cat = id_cat

    def get_id_logement(self) -> int:
        """getter de l'id du logement associé au bien

        Returns:
            int: id du logement
        """
        return self.id_logement

    def set_id_logement(self, id_logement: int) -> None:
        """modifie le logement associé au bien (par son ID)

        Args:
            id_logement (int): id du nouveau logement associé
        """
        self.id_logement = id_logement
    
class Piece(Base):
    __tablename__ = "PIECE"
    
    id_piece = Column(Integer, primary_key=True, nullable=False, name="ID_PIECE")
    nom_piece = Column(String(20), nullable=True, name="NOM_PIECE")
    desc_piece = Column(String(1000), nullable=True, name="DESCRIPTION")
    id_logement = Column(Integer, ForeignKey("LOGEMENT.ID_LOGEMENT"), primary_key=True, nullable=False, name="ID_LOGEMENT")
    
    def __init__(self, id_piece: int, nom_piece: str, desc_piece: str, id_logement: int) -> None:
        """Init d'une pièce dans un logement

        Args:
            id_piece (int): id de la pièce
            nom_piece (str): nom de la pièce
            desc_piece (str): description de la pièce
            id_logement (int): id du logement où est contenu la pièce
        """
        self.id_piece = id_piece
        self.nom_piece = nom_piece
        self.desc_piece = desc_piece
        self.id_logement = id_logement
        
    def __repr__(self) -> str:
        """représentation de la pièce

        Returns:
            str: une chaîne de caractère contenant l'id de la pièce ainsi que son nom
        """
        return "<Piece (%d) %s >" % (self.id_piece, self.nom_piece)
    
    def get_id_piece(self) -> int:
        """getter de l'id de la pièce

        Returns:
            int: id de la pièce
        """
        return self.id_piece
    
    def set_id_piece(self, id_piece: int) -> None:
        """changer le nom de la pièce

        Args:
            id_piece (int): nouvel id de la pièce
        """
        self.id_piece = id_piece
    
    def get_nom_piece(self) -> str:
        """getter du nom de la pièce

        Returns:
            str: nom de la pièce
        """
        return self.nom_piece
    
    def set_nom_piece(self, nom_piece: str) -> None:
        """changer le nom de la pièce

        Args:
            nom_piece (str): Nouveau nom de la pièce 
        """
        self.nom_piece = nom_piece
    
    def get_desc_piece(self) -> str:
        """getter de la description de la pièce 

        Returns:
            str: description de la pièce
        """
        return self.desc_piece
    
    def set_desc_piece(self, desc_piece: str) -> None:
        """changer la description de la pièce 

        Args:
            desc_piece (str): nouvelle description de la pièce
        """
        self.desc_piece = desc_piece
    
    def get_id_logement(self) -> int:
        """getter de l'id du logement de la pièce

        Returns:
            int: id du logement où est contenu la pièce
        """
        return self.id_logement
    
    def set_id_logement(self, id_logement: int) -> None:
        """changer l'id du logement où est contenu la pièce 

        Args:
            id_logement (int): nouvell id du logement
        """
        self.id_logement = id_logement

class TypeBien(Base):
    __tablename__ = "TYPEBIEN"
    
    id_type = Column(Integer, primary_key=True, nullable=False, name="ID_TYPE_BIEN")
    nom_type = Column(String(20), nullable=False, name="NOM_TYPE")
    
    def __init__(self, id_type: int, nom_type: str) -> None:
        """Init d'un type de bien

        Args:
            id_type (int): id du type de bien
            nom_type (str): nom du type de bien
        """
        self.id_type = id_type
        self.nom_type = nom_type
    
    def __repr__(self) -> str:
        """représentation du type de bien

        Returns:
            str: contenant l'id et le nom du type
        """
        return "<TypeBien (%d) %s >" % (self.id_type, self.nom_type)
    
    def get_id_type(self) -> int:
        """getter de l'id du type

        Returns:
            int: l'id du type
        """
        return self.id_type
    
    def set_id_type(self, id_type: int) -> None:
        """changer l'id du type

        Args:
            id_type (int): nouvel id du type (unique)
        """
        self.id_type = id_type
    
    def get_nom_type(self) -> str:
        """getter du nom du type 

        Returns:
            str: nom du type de bien
        """
        return self.nom_type
    
    def set_nom_type(self, nom_type: str) -> None:
        """changer le nom du type

        Args:
            nom_type (str): nouveau nom du type de bien
        """
        self.nom_type = nom_type

class Categorie(Base):
    __tablename__ = "CATEGORIE"
    
    id_cat = Column(Integer, primary_key=True, nullable=False, name="ID_CATEGORIE")
    nom_cat = Column(String(20), nullable=False, name="NOM_CATEGORIE")
    
    def __init__(self, id_cat: int, nom_cat: str) -> None:
        """init d'une catégorie de bien

        Args:
            id_cat (int): id de la catégorie (unique)
            nom_cat (str): nom de la catégorie
        """
        self.id_cat = id_cat
        self.nom_cat = nom_cat
    
    def __repr__(self) -> str:
        """représentation d'une catégorie de bien

        Returns:
            str: contenant l'id et le nom de la catégorie
        """
        return "<Categorie (%d) %s >" % (self.id_cat, self.nom_cat)
    
    def get_id_cat(self) -> int:
        """getter de l'id de la catégorie

        Returns:
            int: 
        """
        return self.id_cat
    
    def set_id_cat(self, id_cat: int) -> None:
        """Modification de l'id

        Args:
            id_cat (int): nouvel id
        """
        self.id_cat = id_cat
    
    def get_nom_cat(self) -> str:
        """getter du nom de la catégorie

        Returns:
            int: 
        """
        return self.nom_cat
    
    def set_nom_cat(self, nom_cat: str) -> None:
        """Modification du nom de la catégorie

        Args:
            nom_cat (str): nouveau nom de la catégorie
        """
        self.nom_cat = nom_cat

class Justificatif(Base):
    __tablename__ = "JUSTIFICATIF"
    
    id_justif = Column(Integer, primary_key=True, name="ID_JUSTIFICATIF")
    nom_justif = Column(String(30), name="NOM_JUSTIFICATIF")
    date_ajout = Column(Date, name="DATE_AJOUT")
    URL = Column(String(200), name="URL")
    id_bien = Column(Integer, ForeignKey("BIEN.ID_BIEN"), primary_key=True, name="ID_BIEN")
    
    def __init__(self, id_justif: int, nom_justif: str, date_ajout: date, URL: str, id_bien: int) -> None:
        """init d'un justificatif

        Args:
            id_justif (int): ID du justificatif (unique)
            nom_justif (str): nom du justificatif
            date_ajout (str): date d'ajout
            URL (str): URL vers l'image du justificatif
            id_bien (int): ID du bien associé au justificatif
        """
        self.id_justif = id_justif
        self.nom_justif = nom_justif
        self.date_ajout = date_ajout
        self.URL = URL
        self.id_bien = id_bien
    
    def __repr__(self) -> str:
        """représentation du justificatif

        Returns:
            str: String contenant l'ID du justificatif, son nom, sa date d'ajout, et le lien vers l'image justificatif, ainsi que l'ID du bien associé
        """
        return "<Justificatif (%d) %s %s %s %d>" % (self.id_justif, self.nom_justif, self.date_ajout, self.URL, self.id_bien)
    
    def get_id_justif(self) -> int:
        """getter de l'ID du justificatif

        Returns:
            int: ID du justificatif
        """
        return self.id_justif
    
    def set_id_justif(self, id_justif: int) -> None:
        """modification de l'ID du justificatif

        Args:
            id_justif (int): nouvel ID du justificatif (unique)
        """
        self.id_justif = id_justif
    
    def get_nom_justif(self) -> str:
        """getter du nom du justificatif

        Returns:
            str: nom du justificatif
        """
        return self.nom_justif
    
    def set_nom_justif(self, nom_justif: str) -> None:
        """Modifie le nom du justificatif

        Args:
            nom_justif (str): nouveau nom du justificatif
        """
        self.nom_justif = nom_justif
    
    def get_date_ajout(self) -> date:
        """getter de la date d'ajout

        Returns:
            str: date de l'ajout du justificatif
        """
        return self.date_ajout
    
    def set_date_ajout(self, date_ajout: date) -> None:
        """modification de la date d'ajout

        Args:
            date_ajout (str): nouvelle date d'ajout
        """
        self.date_ajout = date_ajout
    
    def get_URL(self) -> str:
        """getter de l'URL vers l'image du justificatif

        Returns:
            str: URL vers l'image du justificatif
        """
        return self.URL
    
    def set_URL(self, URL: str) -> None:
        """modifie l'URL vers l'ilage du justificatif

        Args:
            URL (str): nouvel URL
        """
        self.URL = URL
    
    def get_id_bien(self) -> int:
        """getter de l'ID du bien associé

        Returns:
            int: ID du bien associé
        """
        return self.id_bien
    
    def set_id_bien(self, id_bien: int) -> None:
        """modifie le bien auquel est associé le justificatif

        Args:
            id_bien (int): nouvel ID
        """
        self.id_bien = id_bien

class User(Base, UserMixin):
    __tablename__ = "USER"
    
    mail = Column(String(50), primary_key=True, name="MAIL")
    password = Column(String(64), name="PASSWORD")
    role = Column(String(10), name="ROLE")
    id_user = Column(Integer, ForeignKey("PROPRIETAIRE.ID_PROPRIO"), name="ID_PROPRIO")
    proprio = relationship('Proprietaire', back_populates='user', uselist=False)
    
    def get_id(self) -> str:
        """getter du mail

        Returns:
            str:  mail du user
        """
        return self.mail
    
    def set_id(self, mail: str) -> None:
        """modifie le mail du user

        Args:
            mail (str): nouveau mail
        """
        self.mail = mail
    
    def get_password(self) -> str:
        """getter du mot de passe de user

        Returns:
            str: mot de passe de user
        """
        return self.password
    
    def set_password(self, password: str) -> None:
        """modifie le mot de passe de user

        Args:
            password (str): nouveau mot de passe
        """
        self.password = password
    
    def get_role(self) -> str:
        """getter du role de user

        Returns:
            str: role de user
        """
        return self.role
    
    def set_role(self, role: str) -> None:
        """modifie le role de user

        Args:
            role (str): nouveau role de user
        """
        self.role = role
    
    def get_id_user(self) -> int:
        """getter de l'id de user

        Returns:
            int: id de user
        """
        return self.id_user
    
    def set_id_user(self, id_user: int) -> None:
        """modifie l'id de user (unique)

        Args:
            id_user (int): nouvel id de user
        """
        self.id_user = id_user

    @staticmethod
    def modifier(mail: str, nom: str, prenom: str) -> None:
        """modifier le nom et ou prénom d'un propriétaire

        Args:
            mail (str): email actuelle du proprio
            nom (str): nouveau nom (ou actuel si inchangé)
            prenom (str): nouveau prenom (ou actuel si inchangé)
        """
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
