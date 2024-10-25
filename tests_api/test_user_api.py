# python -m unittest tests_api.test_user_api

from unittest import TestCase
from app import app
from models import db, User
from datetime import datetime, timezone

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///calendar-tests'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

db.drop_all()
db.create_all()

USER_DATA = {
    "email": "user1@email.com",
    "password": "password1",
    "f_name": 'Larry',
    "l_name": "Davis"
}
USER_DATA2 = {
    "email": "user2@email.com",
    "password": "password1",
    "f_name": 'Larry',
    "l_name": "Davis"
}

class UserTestCase(TestCase):
    '''Tests for views of User API'''

    def setUp(self):
        '''Make demo data'''
        db.drop_all()
        db.create_all()

        user = User(**USER_DATA)
        
        db.session.add(user)
        db.session.commit()

        self.user = user

    def tearDown(self):
        '''Clean up unsuccessful tests'''
        
        db.session.rollback()
        db.drop_all()


    def test_list_users(self): ############ 01
        '''Test listing Users'''
        with app.test_client() as client:
            resp = client.get("/api/users")

            self.assertEqual(resp.status_code, 200)

            data = resp.json
            self.assertIn('users', data)
            self.assertEqual(len(data["users"]), 1)
            
            user_data = data["users"][0]
            self.assertEqual(user_data["email"], "user1@email.com")
            self.assertEqual(user_data["f_name"], "Larry")
            self.assertEqual(user_data["l_name"], "Davis")
            self.assertEqual(user_data["id"], 1)


    def test_get_user(self): ############ 02
        '''Test getting a User'''
        with app.test_client() as client:
            url = f"/api/users/{self.user.id}"
            resp = client.get(url)

            self.assertEqual(resp.status_code, 200)
            
            data = resp.json
            self.assertIn('user', data)

            user_data = data['user']
            self.assertEqual(user_data["id"], self.user.id)
            self.assertEqual(user_data["email"], self.user.email)
            self.assertEqual(user_data["f_name"], self.user.f_name)
            self.assertEqual(user_data["l_name"], self.user.l_name)
            

    def test_create_user(self): ############ 03
        '''Test creating a new User'''
        with app.test_client() as client:
            url = "/api/users"
            resp = client.post(url, json=USER_DATA2)

            self.assertEqual(resp.status_code, 201)

            data = resp.json
            self.assertIn('user', data)
            self.assertIsInstance(data['user']['id'], int)  #make sure the ID is an integer
            self.assertEqual(data['user']['email'], USER_DATA2['email'])
            self.assertEqual(data['user']['f_name'], USER_DATA2['f_name'])
            self.assertEqual(data['user']['l_name'], USER_DATA2['l_name'])
            self.assertEqual(User.query.count(), 2)

    def test_update_user(self): ############ 04
        '''Test updating email on a User'''
        with app.test_client() as client:
            url = f"/api/users/{self.user.id}"
            resp = client.patch(url, json={"email": "updated@email.com"})
            
            self.assertEqual(resp.status_code, 200)
            
            data = resp.json
            self.assertEqual(data['user']['email'], 'updated@email.com')
            
            
    def test_delete_user(self): ############ 05
        '''Test deleting a User'''
        with app.test_client() as client:
            url = f"/api/users/{self.user.id}"
            resp = client.delete(url)
            
            self.assertEqual(resp.status_code, 200)
            
            data = resp.json
            self.assertEqual(data['message'], 'User has been deleted')
            
            deleted_user = User.query.get(self.user.id)
            self.assertIsNone(deleted_user)
            
