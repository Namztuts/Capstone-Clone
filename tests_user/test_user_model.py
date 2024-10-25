# python -m unittest tests_user.test_user_model

import os
from unittest import TestCase
from sqlalchemy import exc
from sqlalchemy.exc import IntegrityError
from models import db, User, Event, Calendar

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///calendar-tests"

# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data
db.create_all()


class UserModelTestCase(TestCase):
    '''Test Users'''

    def setUp(self):
        '''Create User and Calendar test data'''
        db.drop_all()
        db.create_all()

        self.u_id = 123
        
        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res


    def test_user_register(self): ############## 01
        '''Test that the User register works'''
        
        user = User.register("testing@email.com", "testing123", 'Test', 'Ing')
        self.assertIsNotNone(user)
        
        db.session.add(user)
        db.session.commit()
        
        db_user = User.query.filter_by(email="testing@email.com").first()
        self.assertIsNotNone(db_user)
        
    def test_user_db(self): ############## 02
        '''Test that the User gets added correctly to DB'''
        
        user = User.register("testing@email.com", "testing123", 'Test', 'Ing')
        user.id = self.u_id
        
        db.session.add(user)
        db.session.commit()
        
        db_user = User.query.get(user.id)
        self.assertIsNotNone(db_user)
        
        self.assertEqual(db_user.email, "testing@email.com")
        self.assertEqual(db_user.f_name, 'Test')
        self.assertEqual(db_user.l_name, 'Ing')
        self.assertTrue(db_user.password.startswith("$2b$")) #NOTE: Bcrypt strings should start with $2b$
        
    def test_invalid_email_register(self): ############## 03
        '''Test invalid registration with no email | should result in error'''
        
        invalid = User.register(None, "testing123", 'Test', 'Ing')
        invalid.id = self.u_id
        
        self.assertRaises(IntegrityError)

    def test_duplicate_email_registration(self): ############## 04
        '''Test duplicate email registration | should result in error'''
        
        User.register("dupe@email.com", "testing123", 'Test', 'Ing')
        db.session.commit()  #add the first user
        User.register("dupe@email.com", "dupe123", 'Dupe', 'User')
        db.session.commit() #try to add the second with the same email
        
        self.assertRaises(IntegrityError)
        
    def test_user_deletion(self): ############## 05
        '''Test that a user gets deleted from DB'''
        
        user = User.register("delete@email.com", "testing123", 'Test', 'Ing')
        user.id = self.u_id
        db.session.add(user)
        db.session.commit()
        db.session.delete(user)
        db.session.commit()
        
        deleted_user = User.query.get(user.id)
        self.assertIsNone(deleted_user)
            