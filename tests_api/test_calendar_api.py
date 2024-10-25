# python -m unittest tests_api.test_calendar_api

from unittest import TestCase
from app import app
from models import db, User, Calendar

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
CAL_DATA = {
    'name':"Personal",
    'description':"Calendar for personal events",
    'owner_id':1
}
CAL_DATA2 = {
    'name':"Personal",
    'description':"Calendar for personal events",
    'is_public':False,
    "created_at": "2024-10-23T12:00:00",
    'owner_id':1
}


class CalendarTestCase(TestCase):
    '''Tests for views of Calendar API'''

    def setUp(self):
        '''Make demo data'''
        db.drop_all()
        db.create_all()

        user = User(**USER_DATA)
        calendar = Calendar(**CAL_DATA)
        
        db.session.add_all([user, calendar])
        db.session.commit()

        self.user = user
        self.calendar = calendar

    def tearDown(self):
        '''Clean up unsuccessful tests'''
        
        db.session.rollback()
        db.drop_all()


    def test_list_calendars(self): ############ 01
        '''Test listing Calendars'''
        with app.test_client() as client:
            resp = client.get("/api/calendars")

            self.assertEqual(resp.status_code, 200)

            data = resp.json
            self.assertIn('calendars', data)
            self.assertEqual(len(data["calendars"]), 1)
            
            calendar_data = data["calendars"][0]
            self.assertEqual(calendar_data["name"], "Personal")
            self.assertEqual(calendar_data["description"], "Calendar for personal events")
            self.assertEqual(calendar_data["id"], 1)


    def test_get_calendar(self): ############ 02
        '''Test getting a Calendar'''
        with app.test_client() as client:
            url = f"/api/calendars/{self.calendar.id}"
            resp = client.get(url)

            self.assertEqual(resp.status_code, 200)
            
            data = resp.json
            self.assertIn('calendar', data)

            calendar_data = data['calendar']
            self.assertEqual(calendar_data["id"], self.calendar.id)
            self.assertEqual(calendar_data["name"], self.calendar.name)
            self.assertEqual(calendar_data["description"], self.calendar.description)
            

    def test_create_calendar(self): ############ 03
        '''Test creating a new Calendar'''
        with app.test_client() as client:
            url = "/api/calendars"
            resp = client.post(url, json=CAL_DATA2)

            self.assertEqual(resp.status_code, 201)

            data = resp.json
            self.assertIn('calendar', data)
            self.assertIsInstance(data['calendar']['id'], int)  #make sure the ID is an integer
            self.assertEqual(data['calendar']['name'], CAL_DATA2['name'])
            self.assertEqual(data['calendar']['description'], CAL_DATA2['description'])
            self.assertEqual(data['calendar']['is_public'], CAL_DATA2['is_public'])
            self.assertEqual(Calendar.query.count(), 2)

    def test_update_calendar(self): ############ 04
        '''Test updating email on a Calendar'''
        with app.test_client() as client:
            url = f"/api/calendars/{self.calendar.id}"
            resp = client.patch(url, json={"name": "Updated"})
            
            self.assertEqual(resp.status_code, 200)
            
            data = resp.json
            self.assertEqual(data['calendar']['name'], 'Updated')
            
            
    def test_delete_calendar(self): ############ 05
        '''Test deleting a Calendar'''
        with app.test_client() as client:
            url = f"/api/calendars/{self.calendar.id}"
            resp = client.delete(url)
            
            self.assertEqual(resp.status_code, 200)
            
            data = resp.json
            self.assertEqual(data['message'], 'Calendar has been deleted')
            
            deleted_calendar = Calendar.query.get(self.calendar.id)
            self.assertIsNone(deleted_calendar)
            
