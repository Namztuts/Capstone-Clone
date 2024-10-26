from flask import Flask, request, jsonify, Blueprint
from models import connect_db, db, Calendar, Event
import os

app = Flask(__name__)
api_calendars= Blueprint('api_calendars', __name__) #creating the API blueprint

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "oh-so-secret")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SUPABASE_URL", "postgresql:///calendar")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# app.app_context().push()
connect_db(app)


#############################################
#              CALENDAR ROUTES              #
#############################################

@api_calendars.route('/api/calendars')
def list_calendars():
    '''Returns JSON for all calendars'''
    
    calendars = Calendar.query.all()
    calendars_JSON = [calendar.serialize() for calendar in calendars]
    response_JSON = jsonify(calendars=calendars_JSON)
    
    return (response_JSON)


@api_calendars.route('/api/calendars/<int:id>')
def get_calendar(id):
    '''Returns JSON for a specific calendar'''
    
    calendar = Calendar.query.get_or_404(id)
    calendar_JSON = calendar.serialize()
    response_JSON = jsonify(calendar=calendar_JSON)
    
    return (response_JSON)


@api_calendars.route('/api/calendars', methods=['POST'])
def create_calendar():
    '''Creates a new calendar and return JSON'''
    
    name = request.json['name']
    description = request.json['description']
    is_public = request.json['is_public']
    created_at = request.json['created_at']
    
    owner_id = request.json['owner_id']
    
    new_calendar = Calendar(name=name, description=description, is_public=is_public, created_at=created_at, owner_id=owner_id)
    
    db.session.add(new_calendar)
    db.session.commit()
    
    new_calendar_JSON = new_calendar.serialize()
    response_JSON = jsonify(calendar=new_calendar_JSON)
    
    return (response_JSON, 201)


@api_calendars.route('/api/calendars/<int:id>', methods=['PATCH'])
def update_calendar(id):
    '''Updates a specific calendar and returns JSON'''
    
    calendar = Calendar.query.get_or_404(id)
    
    calendar.name = request.json.get('name', calendar.name)
    calendar.description = request.json.get('description', calendar.description)
    calendar.is_public = request.json.get('is_public', calendar.is_public)
    
    calendar.owner_id = request.json.get('owner_id', calendar.owner_id)
    
    db.session.commit()
    
    calendar_JSON = calendar.serialize()
    response_JSON = jsonify(calendar=calendar_JSON)
    
    return (response_JSON)


@api_calendars.route('/api/calendars/<int:id>', methods=['DELETE'])
def delete_calendar(id):
    '''Deletes a specific calendar and returns deletion confirmation'''
    
    calendar = Calendar.query.get_or_404(id)
    
    db.session.delete(calendar)
    db.session.commit()
    
    response_JSON = jsonify(message='Calendar has been deleted')
    
    return (response_JSON)


#############################################
#              CALENDAR EVENTS              #
#############################################

@api_calendars.route('/api/calendars/<int:id>/events')
def get_calendar_events(id):
    '''Returns JSON for events for a specific calendar'''
    
    calendar = Calendar.query.get_or_404(id) #chekc if the calendar exists in the DB
    events = Event.query.filter(Event.calendar_id == id).all()
        
    events_JSON = [event.serialize() for event in events]
    response_JSON = jsonify(events=events_JSON)
    
    return (response_JSON)