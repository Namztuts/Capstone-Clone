# python -m unittest tests_calendar.test_calendar_model

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


class CalendarModelTestCase(TestCase):
    '''Calendar Events'''

    def setUp(self):
        '''Create User and Event test data'''
        db.drop_all()
        db.create_all()

        self.u_id = 123
        self.c_id = 789
        
        user = User.register("testing@email.com", "testing123", 'Test', 'Ing')
        user.id = self.u_id
        
        db.session.add(user)
        db.session.commit()

        self.user = User.query.get(self.u_id)

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res


    def test_calendar_model(self): ############## 01
        '''Test that the Calendar model works'''
        
        calendar = Calendar(
            name="Personal",
            owner_id=self.u_id
            )

        db.session.add(calendar)
        db.session.commit()

        # User should have 1 calendar
        self.assertEqual(len(self.user.calendars), 1)
        self.assertEqual(self.user.calendars[0].name, "Personal")
        
    def test_calendar_missing_name(self): ############## 02
        '''Test a missing Name (required field) | should result in error'''
        
        with self.assertRaises(IntegrityError):
            calendar = Calendar(
                owner_id=self.u_id
                )
            
            db.session.add(calendar)
            db.session.commit()
            
    def test_event_delete(self): ############## 03
        '''Test Calendar deletion'''
        
        calendar = Calendar(
            name="Personal",
            owner_id=self.u_id
            )
    
        db.session.add(calendar)
        db.session.commit()

        db.session.delete(calendar)
        db.session.commit()

        self.assertIsNone(Calendar.query.get(calendar.id))
