# python -m unittest tests_event.test_event_model

import os
from unittest import TestCase
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


class EventModelTestCase(TestCase):
    '''Test Events'''

    def setUp(self):
        '''Create User and Calendar test data'''
        db.drop_all()
        db.create_all()

        self.u_id = 123
        self.c_id = 789
        
        user = User.register("testing@email.com", "testing123", 'Test', 'Ing')
        user.id = self.u_id
        
        calendar = Calendar(name="Test Calendar", owner_id=self.u_id)
        calendar.id = self.c_id
        
        db.session.add_all([user, calendar])
        db.session.commit()

        self.user = User.query.get(self.u_id)
        self.calendar = Calendar.query.get(self.c_id)

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res


    def test_event_model(self): ############## 01
        '''Test that the Event model works'''
        
        event = Event(
            title="Dentist",
            start_time='2024-12-12',
            end_time='2024-12-12',
            calendar_id=self.c_id,
            creator_id=self.u_id
            )

        db.session.add(event)
        db.session.commit()

        # User should have 1 event
        self.assertEqual(len(self.user.events), 1)
        self.assertEqual(self.user.events[0].title, "Dentist")
        
    def test_event_end_time(self): ############## 02
        '''Test that the end time is after start time | should result in error'''
        
        with self.assertRaises(ValueError, msg="End time must be after start time"):
            
            event = Event(
                title="Oil Change",
                start_time='2024-12-13',
                end_time='2024-12-12',
                calendar_id=self.c_id,
                creator_id=self.u_id
                )
            
            db.session.add(event)
            db.session.commit()
            
    def test_event_missing_title(self): ############## 03
        '''Test a missing Title (required field) | should result in error'''
        
        with self.assertRaises(IntegrityError):
            event = Event(
                start_time='2024-12-12',
                end_time='2024-12-12',
                calendar_id=self.c_id,
                creator_id=self.u_id
                )
            
            db.session.add(event)
            db.session.commit()
            
    def test_event_delete(self): ############## 04
        '''Test Event deletion'''
        
        event = Event(
            title="Voting",
            start_time='2024-12-12',
            end_time='2024-12-12',
            calendar_id=self.c_id,
            creator_id=self.u_id
        )
    
        db.session.add(event)
        db.session.commit()

        db.session.delete(event)
        db.session.commit()

        self.assertIsNone(Event.query.get(event.id))
        
    def test_event_all_day(self): ############## 05
        '''Test all_day selection'''
    
        event = Event(
            title="Conference",
            start_time='2024-12-12',
            end_time='2024-12-12',
            all_day=True,
            calendar_id=self.c_id,
            creator_id=self.u_id
        )
    
        db.session.add(event)
        db.session.commit()

        self.assertTrue(event.all_day)
