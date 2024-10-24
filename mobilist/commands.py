import click
from .app import app, db
from .models import *
from datetime import *
import yaml

#Commande de creation de table
@app.cli.command()
def syncdb():
    db.create_all()

#Commande de chargement de donnée via un fichier yml + creation tables
@app.cli.command()
@click.argument('filename')
def loaddb(filename):
    db.drop_all()
    db.create_all()
    data = yaml.load(open(filename), Loader=yaml.SafeLoader)
    session = db.session
    date_format = '%Y-%m-%d'
    for entity in data:
        match entity['TYPE']:
            case 'PROPRIETAIRE':
                new_proprietaire = Proprietaire(
                    idProprio=entity['ID_PROPRIETAIRE'], 
                    nom = entity['NOM'],
                    prenom = entity['PRENOM'])
                session.add(new_proprietaire)
            case 'LOGEMENT':
                new_logement = Logement(
                    idLogement=entity['ID_LOGEMENT'],
                    typeL = entity['TYPE_LOGEMENT'],
                    adresse = entity['ADRESSE'],
                    descriptionLogement = entity['DESCRIPTION'])
                session.add(new_logement)
            case 'PIECE':
                new_piece = Piece(
                    idPiece = entity['ID_PIECE'],
                    nomPiece = entity['NOM_PIECE'],
                    descriptionPiece = entity['DESCRIPTION'],
                    idLogement = entity['ID_LOGEMENT']
                )
                session.add(new_piece)
            case 'CATEGORIE_BIEN':
                new_categorie = Categorie(
                    idCat = entity['ID_CATEGORIE'],
                    nomCat = entity['NOM_CATEGORIE']
                )
                session.add(new_categorie)
            case 'TYPE_BIEN':
                new_typeB = TypeBien(
                    idType = entity['ID_TYPE'],
                    nomType = entity['NOM_TYPE']
                )
                session.add(new_typeB)
            case 'BIEN':
                date = datetime.strptime(entity['DATE_ACHAT'], date_format)
                new_bien = Bien(
                    idBien = entity['ID_BIEN'],
                    nomB = entity['NOM_BIEN'],
                    dateAchat = date.date(),
                    prix = entity['PRIX'],
                    idPiece = entity['ID_PIECE'],
                    idType = entity['ID_TYPE_BIEN'],
                    idCat = entity['ID_CATEGORIE'] 
                )
                session.add(new_bien)
            case 'JUSTIFICATIF':
                # datetime.datetime.now()
                # entity['DATE_AJOUT']
                date = datetime.strptime(entity['DATE_AJOUT'], date_format)
                new_justificatif = Justificatif(
                    idJustif = entity['ID_JUSTIFICATIF'],
                    nomJustif = entity['NOM_JUSTIFICATIF'],
                    dateAjout = date,
                    URL = entity['URL'],
                    idBien = entity['ID_BIEN']
                )
                session.add(new_justificatif)
            case 'AVIS':
                new_avis = Avis(
                    idAvis = entity['ID_AVIS'],
                    descriptionAvis = entity['DESCRIPTION'],
                    idProprio = entity['ID_PROPRIETAIRE']
                )
                session.add(new_avis)
            case 'AVOIR':
                new_avoir = AVOIR(
                    idP = entity['ID_PROPRIETAIRE'],
                    idL = entity['ID_LOGEMENT']
                )
                session.add(new_avoir)
        db.session.commit()
    print(f"loaded file: {filename}")

   

@app.cli.command()
@click.argument('mail')
@click.argument('password')
@click.argument('role')
def newuser(mail, password, role):
    from.models import User
    from hashlib import sha256
    m = sha256()
    m.update(password.encode())
    id = None
    if role != "admin":
        proprio = Proprietaire(idProprio=id)
        id = int(max_id())+1
        db.session.add(proprio)
    u = User(mail=mail, password=m.hexdigest(), role=role, id_user=id)
    db.session.add(u)
    db.session.commit()
    
@app.cli.command()
@click.argument('mail')
@click.argument('password')
def passwd(mail, password):
    from.models import User
    from hashlib import sha256
    m = sha256()
    m.update(password.encode())
    u = User.query.get(mail)
    u.password = m.hexdigest()
    db.session.commit()