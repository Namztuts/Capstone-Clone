# python -m unittest tests_api.test_calendar_api

from unittest import TestCase
from app import app
from models import db, User, Calendar, Event

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
EVENT_DATA = {
    'title':"Dentist",
    'description':"Teeth Cleaning",
    'start_time':'2024-10-23T12:00',
    'end_time':'2024-10-23T12:00',
    'location':'Family Dentist',
    'calendar_id':1,
    'creator_id':1
}
EVENT_DATA2 = {
    'title':"Dentist",
    'description':"Teeth Cleaning",
    'start_time':'2024-10-23T12:00',
    'end_time':'2024-10-23T12:00',
    'location':'Family Dentist',
    'bg_color':'#e1e1e1',
    'txt_color':'#000000',
    'all_day':False,
    'calendar_id':1,
    'creator_id':1
}

class EventTestCase(TestCase):
    '''Tests for views of Event API'''

    def setUp(self):
        '''Make demo data'''
        db.drop_all()
        db.create_all()

        user = User(**USER_DATA)
        calendar = Calendar(**CAL_DATA)
        event = Event(**EVENT_DATA)
        
        db.session.add_all([user, calendar, event])
        db.session.commit()

        self.user = user
        self.calendar = calendar
        self.event = event

    def tearDown(self):
        '''Clean up unsuccessful tests'''
        
        db.session.rollback()
        db.drop_all()


    def test_list_events(self): ############ 01
        '''Test listing Events'''
        with app.test_client() as client:
            resp = client.get("/api/events")

            self.assertEqual(resp.status_code, 200)

            data = resp.json
            self.assertIn('events', data)
            self.assertEqual(len(data["events"]), 1)
            
            event_data = data["events"][0]
            self.assertEqual(event_data["title"], "Dentist")
            self.assertEqual(event_data["description"], "Teeth Cleaning")
            self.assertEqual(event_data["start_time"], "2024-10-23T12:00")
            self.assertEqual(event_data["end_time"], "2024-10-23T12:00")
            self.assertEqual(event_data["location"], "Family Dentist")
            self.assertEqual(event_data["id"], 1)


    def test_get_event(self): ############ 02
        '''Test getting a Event'''
        with app.test_client() as client:
            url = f"/api/events/{self.event.id}"
            resp = client.get(url)

            self.assertEqual(resp.status_code, 200)
            
            data = resp.json
            self.assertIn('event', data)

            event_data = data['event']
            #convert the start/end times to the expected format
            expected_start_time = self.event.start_time.strftime('%Y-%m-%dT%H:%M')
            expected_end_time = self.event.end_time.strftime('%Y-%m-%dT%H:%M')
            
            self.assertEqual(event_data["id"], self.event.id)
            self.assertEqual(event_data["title"], self.event.title)
            self.assertEqual(event_data["description"], self.event.description)
            self.assertEqual(event_data["start_time"], expected_start_time)
            self.assertEqual(event_data["end_time"], expected_end_time)
            self.assertEqual(event_data["location"], self.event.location)
            

    def test_create_event(self): ############ 03
        '''Test creating a new Event'''
        with app.test_client() as client:
            url = "/api/events"
            resp = client.post(url, json=EVENT_DATA2)

            self.assertEqual(resp.status_code, 201)

            data = resp.json
            self.assertIn('event', data)
            self.assertIsInstance(data['event']['id'], int)  #make sure the ID is an integer
            self.assertEqual(data['event']['title'], EVENT_DATA2['title'])
            self.assertEqual(data['event']['description'], EVENT_DATA2['description'])
            self.assertEqual(data['event']['start_time'], EVENT_DATA2['start_time'])
            self.assertEqual(data['event']['end_time'], EVENT_DATA2['end_time'])
            self.assertEqual(data['event']['bg_color'], EVENT_DATA2['bg_color'])
            self.assertEqual(data['event']['txt_color'], EVENT_DATA2['txt_color'])
            self.assertEqual(data['event']['all_day'], EVENT_DATA2['all_day'])
            self.assertEqual(Calendar.query.count(), 1)

    def test_update_event(self): ############ 04
        '''Test updating email on a Event'''
        with app.test_client() as client:
            url = f"/api/events/{self.event.id}"
            resp = client.patch(url, json={"title": "Updated Title"})
            
            self.assertEqual(resp.status_code, 200)
            
            data = resp.json
            self.assertEqual(data['event']['title'], 'Updated Title')
            
            
    def test_delete_event(self): ############ 05
        '''Test deleting a Event'''
        with app.test_client() as client:
            url = f"/api/events/{self.event.id}"
            resp = client.delete(url)
            
            self.assertEqual(resp.status_code, 200)
            
            data = resp.json
            self.assertEqual(data['message'], 'Event has been deleted')
            
            deleted_event = Event.query.get(self.event.id)
            self.assertIsNone(deleted_event)
            
