# projet-finale_BUT-info
Groupe : Akhtar Naima, Bocquet Clemence, Randrianstoa Nathan, Valin Ophelie, Vilcoq Yohann

## Table des matières 
- Introduction
  * Le sujet
  * L'application
- Lancement application

## Introduction
> Différents types d’intempéries laissent des dégâts irréversibles sur des biens matériels d’un logement. Ces dommages sont souvent garantis par une assurance habitation.  
>  Toutefois, pour faire constater les dégâts d’événements météorologiques, il est nécessaire de réaliser une démarche auprès de l’assureur listant l’ensemble des dommages subis et des justificatifs d’achat associés.

> MobiList est une application de gestion de biens matériels d’un logement. Celle-ci va permettre d’informatiser ce processus en dressant un inventaire des biens par pièces, de conserver les preuves d’achats et de calculer l’usure du bien au moment du dommage.
> Ainsi, lors de dégâts subis, l’application permettra de fournir un état financier des possibles pertes en fonction de leur vétusté et d’afficher les justificatifs d’achats associés.


## Lancement application
Pour lancer un environnement virtuel, vous devez, depuis VSCode : 
### Si un .venv/venv se trouve dans le projet 
> Ouvrir le projet à sa racine, lancer la commande **source venv/bin/activate**  
> Avant le prompt, un (.venv) doit être affiché affirmant que vous avez bien activé votre environnement virtuel  

### Si il n'y a pas de .venv/venv ou qu'il y a des difficultés à activer le venv
> Sur VSCode, ouvrir le projet à sa racine  
> Aller dans mobilist>app.py  
> Sélectionner un interpréteur (en bas à droite à côté de "Python")  
> Cliquer sur "créer un environnement virtuel" puis "Venv", "supprimer et recreer" et choisir l'interpréteur python  
> Prendre requirement.txt pour les dépendances à  installer  

### Ou bien installation d'un venv via l'interpreteur de commandes (CMD)
> Ouvrez un un shell dans le repertoire racine du project
> Taper la commande `python3 -m venv /path/to/new/virtual/environment` si vous avez la version 3 de python sinon `python3 -m venv /path/to/new/virtual/environment`, une fois le venv de crée veillez l'activer (commande ci-dessus)

### Si lec commandes ci-dessus ne fonctionnent pas
> Si les commande ci-dessus ne fonctionnent pas cette commande peut fonctionner ` virtualenv -p python3 venv`

### Installation des dépendence 
> Dans le répertoire racine du projet il y a un fichier `requirements.txt`, tourjours dans le shell et avec le venv d'activé taper la commande `pip install -r path/to/requirements.txt`. Une fois les dépendences d'installées, vous pouvez lancez l'application.

Pour lancer l'application après avoir activé votre environnement virtuel, depuis VSCode :
### Lancer l'application
> Vous pouvez lancer l'application avec **flask run**  
> Ouvrir la page depuis le lien donné (Running on http://127.0...)

