import unittest
from mobilist.models import User, Proprietaire, Avis, Bien, set_base
from flask import Flask
from flask_sqlalchemy  import SQLAlchemy
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
# from .secure_constante import *
import os
from mobilist.app import app, db


class UserTest(unittest.TestCase):

   def setUp(self):
      with app.app_context():
         app.config['TESTING'] = True
         app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
         client = app.test_client()
         db.drop_all()
         db.create_all()  
        
   def test_proprietaire(self):
      with app.app_context():
         proprio = Proprietaire(1, "John", "Kevin")
         user = User("johnkevin@email.com", "lol123", "proprietaire", 1)
         db.session.add(proprio, user)
         db.session.commit()
         
         proprio_john  = Proprietaire.query.get(1)
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

   def test_user(self):
      with app.app_context():
         proprio = Proprietaire(2, "Martin", "Trixy")
         user = User("trixymartin@email.com", "lol123", "proprietaire", 2)
         
         db.session.add(proprio, user)
         db.session.commit()
         
         self.assertEqual(user.get_id(), "trixymartin@email.com")
         user.set_id("trixymartin2@email.com")
         self.assertEqual(user.get_id(), "trixymartin2@email.com")
         print(user.get_id())

         self.assertEqual(user.get_role(), "proprietaire")
         user.set_role("administrateur")
         self.assertEqual(user.get_role(), "administrateur")
         
         User.modifier("trixymartin2@email.com", "Valin", "Ophelie")
         self.assertEqual(proprio.get_nom(), "Valin")
         self.assertEqual(proprio.get_prenom(), "Ophelie")
         

if __name__ == '__main__':
   unittest.main()