import unittest
from mobilist.models import User, Proprietaire, Categorie, Avis, Bien, Piece, TypeBien, Logement, set_base
from flask import Flask
from flask_sqlalchemy  import SQLAlchemy
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
import datetime
from flask import session
import pytest
# from .secure_constante import *
import os
from mobilist.app import mkpath, app, db


class UserTest(unittest.TestCase):

   def setUp(self):
      with app.app_context():
        self.db_uri = ('sqlite:///'+mkpath('DBMOBILIST.db'))
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = self.db_uri
        self.app = app.test_client()
        set_base(db)
        db.drop_all()
        db.create_all()
        
   def test_proprietaire(self):
      with app.app_context():
         proprio = Proprietaire(1,"johnkevin@email.com", "John", "Kevin")
         user = User("johnkevin@email.com", "lol123", "proprietaire", 1)
         Proprietaire.put_proprio(proprio)
         User.put_user(user)
         
         proprio_john  = db.session.get(Proprietaire,1)
         self.assertEqual(proprio.nom, proprio_john.nom)
         self.assertEqual(proprio_john.nom, "John")
         self.assertEqual(proprio_john.prenom, "Kevin")

         self.assertEqual(proprio.get_id_proprio(), 1)
         self.assertEqual(proprio.get_nom(), "John")
         self.assertEqual(proprio.get_prenom(), "Kevin")
         
         proprio.set_prenom("Patrick")
         self.assertEqual(proprio.get_prenom(), "Patrick")
         proprio.set_nom("Dupont")
         self.assertEqual(proprio.get_nom(), "Dupont")
         self.assertEqual( Proprietaire.max_id(),1)

   def test_user(self):
      with app.app_context():
         proprio = Proprietaire(2,"trixymartin@email.com", "Martin", "Trixy")
         user = User("trixymartin@email.com", "lol123", "proprietaire", 2)
         
         Proprietaire.put_proprio(proprio)
         User.put_user(user)
         user.set_proprio(proprio)

         self.assertEqual(user.get_role(), "proprietaire")
         user.set_role("administrateur")
         self.assertEqual(user.get_role(), "administrateur")
         
         User.modifier("trixymartin@email.com", "Valin", "Ophelie")
         self.assertEqual(proprio.get_nom(), "Valin")
         self.assertEqual(proprio.get_prenom(), "Ophelie")
         
   def test_bien(self):
      with app.app_context():
         logement = Logement(1,"maison 1","MAISON","1 rue","grande maison")
         piece = Piece(1,"salon","grande piece",1)
         typebien = TypeBien(1,"meuble")
         cat = Categorie(1,"meuble")
         bien = Bien(1,"chaise",2,datetime.date(2024, 11, 12), 19.99, 1,1,1,1)
         TypeBien.put_type(typebien)
         Categorie.put_categorie(cat)
         Logement.put_logement(logement)
         Piece.put_piece(piece)
         Bien.put_bien(bien)
         
         self.assertEqual(bien.get_date_achat(), datetime.date(2024, 11, 12))
         self.assertEqual(bien.get_id_bien(), 1)
         self.assertEqual(bien.get_prix(), 19.99)
         self.assertEqual(bien.get_id_cat(),1)
         self.assertEqual(bien.get_nom_bien(), "chaise")
      
   def test_logement(self):
      with app.app_context():
         logement = Logement(2,"maison 2","MAISON","2 rue","grande maison")
         self.assertEqual(logement.get_adresse_logement(), "2 rue")
         self.assertEqual(logement.get_id_logement(),2)
         self.assertEqual(logement.get_type_logement(), "MAISON")
         self.assertEqual(logement.get_desc_logement(), "grande maison") 
         
   def test_piece(self):
      with app.app_context():
         piece = Piece(2,"garage","grande piece",1)
         self.assertEqual(piece.get_desc_piece(), "grande piece")
         self.assertEqual(piece.get_id_piece(), 2)
         self.assertEqual(piece.get_nom_piece(), "garage")
         self.assertEqual(piece.get_id_logement(),1)
   
   def test_typebien(self):
      with app.app_context():
         typebien = TypeBien(2,"électroménager")
         self.assertEqual(typebien.get_id_type(), 2)
         self.assertEqual(typebien.get_nom_type(), "électroménager")
   
   def test_categorie(self):
      with app.app_context():
         cat = Categorie(2, "accessoire cuisine")
         self.assertEqual(cat.get_id_cat(),2)
         self.assertEqual(cat.get_nom_cat(), "accessoire cuisine")
      
   
               
         

if __name__ == '__main__':
   unittest.main()