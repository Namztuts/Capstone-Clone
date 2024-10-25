from datetime import datetime, timezone
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import validates
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    '''Connect to database.'''
    with app.app_context():
        db.app = app
        db.init_app(app)
        db.create_all()
    
    
def add_to_db(object):
    '''Add the user to the database, handle errors if email already exists'''
    db.session.add(object)
    try:
        db.session.commit()
        return object
    except IntegrityError:
        db.session.rollback()
        return None

def create_user(form):
    '''Create a new user from the registration form data'''
    email = form.email.data
    password = form.password.data
    f_name = form.f_name.data
    l_name = form.l_name.data
    new_user = User.register(email, password, f_name, l_name)
    
    return add_to_db(new_user)

def create_event(form, user, calendar):
    '''Create a new event from the registration form data'''
    title = form.title.data
    description = form.description.data
    start_time = form.start_time.data
    end_time = form.end_time.data
    location = form.location.data
    bg_color = form.bg_color.data
    txt_color = form.txt_color.data
    all_day = form.all_day.data
    
    calendar_id = calendar[0]
    creator_id = user.id
    
    new_event = Event(title=title, description=description, start_time=start_time, end_time=end_time, location=location, bg_color=bg_color, txt_color=txt_color, 
                        all_day=all_day, creator_id=creator_id, calendar_id=calendar_id)
    
    return add_to_db(new_event)


class User(db.Model):
    '''Users within the calendar app'''
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    f_name = db.Column(db.String(40), nullable=False)
    l_name = db.Column(db.String(40), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    calendars = db.relationship('Calendar', backref='owner', cascade='all, delete-orphan') #NOTE: might add multiple canlendar function later
    events = db.relationship('Event', backref='creator', cascade='all, delete-orphan')
    
    
    @classmethod #genereates a new instance of User
    def register(cls, email, password, f_name, l_name):
        '''Register user w/hashed password & return user'''

        hashed = bcrypt.generate_password_hash(password) #turns user input password into hash+salt
        hashed_utf8 = hashed.decode("utf8") #turn bytestring into normal (unicode utf8) string

        return cls(email=email, password=hashed_utf8, f_name=f_name, l_name=l_name)
        #return instance of user w/username and hashed pwd | cls (.self) same as User here in a classmethod

    @classmethod
    def authenticate(cls, email, password):
        '''Validate that user exists & password is correct | Return user if valid; else return False'''
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password): #user.password is from db | password is from the user input form
            
            return user #return user instance
        else:
            return False
    
    def serialize(self):
        '''Returns a dictionary representation which we can turn into JSON'''
        return {
            'id': self.id,
            'email': self.email,
            'f_name': self.f_name,
            'l_name': self.l_name,
            'created_at': self.created_at
        }
        
    def full_name(self):
        '''Returns User's full name'''
        first = self.f_name
        last = self.l_name
        
        return (f'{first} {last}')


class Event(db.Model):
    '''Events within the calendar'''
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(100))
    bg_color = db.Column(db.String(7), default="#e1e1e1")
    txt_color = db.Column(db.String(7), default="#000000")
    all_day = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    calendar_id = db.Column(db.Integer, db.ForeignKey('calendars.id'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    @validates('end_time')
    def validate_end_time(self, key, end_time):
        """Ensure end_time is after start_time."""
        if end_time < self.start_time:
            raise ValueError("End time must be after start time")
        return end_time
    
    def serialize(self):
        '''Returns a dictionary representation which we can turn into JSON'''
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'start_time': self.start_time.strftime('%Y-%m-%dT%H:%M'), #ISO format for fullCalendar display
            'end_time': self.end_time.strftime('%Y-%m-%dT%H:%M'),
            'location': self.location,
            'bg_color': self.bg_color,
            'txt_color': self.txt_color,
            'all_day': self.all_day,
            'created_at': self.created_at.strftime('%Y-%m-%dT%H:%M'),
            'calendar_id': self.calendar_id,
            'creator_id': self.creator_id,
        }


class Calendar(db.Model):
    '''Calendar container for organizing events'''
    __tablename__ = 'calendars'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    events = db.relationship('Event', backref='calendar', cascade='all, delete-orphan')
    
    def serialize(self):
        '''Returns a dictionary representation which we can turn into JSON'''
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_public': self.is_public,
            'created_at': self.created_at,
            'owner_id': self.owner_id,
        }
