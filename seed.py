from app import app
from models import db, User, Event, Calendar

db.drop_all()
db.create_all()

user1 = User(
    email="user1@email.com",
    password="password1",
    f_name='Larry',
    l_name='Davis'
)

calendar = Calendar(
    name="Personal",
    description="Calendar for personal events",
    owner_id=1
)

event1 = Event(
    title="Dentist",
    description="Teeth Cleaning",
    start_time='2024-12-12',
    end_time='2024-12-12',
    location='Family Dentist',
    calendar_id=1,
    creator_id=1
)
event2 = Event(
    title="Oil Change",
    description="Changing oil for car",
    start_time='2024-11-01',
    end_time='2024-11-01',
    location='Honda Service',
    calendar_id=1,
    creator_id=1
)

db.session.add_all([user1])
db.session.add_all([calendar])
db.session.add_all([event1, event2])
db.session.commit()