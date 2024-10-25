from flask import Flask, request, jsonify, Blueprint
from models import connect_db, db, Event

app = Flask(__name__)
api_events= Blueprint('api_events', __name__) #creating the API blueprint

app.config["SECRET_KEY"] = "oh-so-secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///calendar"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.app_context().push()
connect_db(app)


##########################################
#              EVENT ROUTES              #
##########################################

@api_events.route('/api/events')
def list_events():
    '''Returns JSON for all events'''
    
    events = Event.query.all()
    events_JSON = [event.serialize() for event in events]
    response_JSON = jsonify(events=events_JSON)
    
    return (response_JSON)


@api_events.route('/api/events/<int:id>')
def get_event(id):
    '''Returns JSON for a specific event'''
    
    event = Event.query.get_or_404(id)
    event_JSON = event.serialize()
    response_JSON = jsonify(event=event_JSON)
    
    return (response_JSON)


@api_events.route('/api/events', methods=['POST'])
def create_event():
    '''Creates a new event and return JSON'''
    
    title = request.json['title']
    description = request.json['description']
    start_time = request.json['start_time']
    end_time = request.json['end_time']
    location = request.json['location']
    bg_color = request.json['bg_color']
    txt_color = request.json['txt_color']
    all_day = request.json['all_day']
    
    creator_id = request.json['creator_id']
    calendar_id = request.json['calendar_id']
    
    #NOTE: don't need the 'create_at' here, but it does get sent through JSON
    new_event = Event(title=title, description=description, start_time=start_time, end_time=end_time, location=location, bg_color=bg_color, txt_color=txt_color, 
                        all_day=all_day, creator_id=creator_id, calendar_id=calendar_id)
    
    db.session.add(new_event)
    db.session.commit()
    
    new_event_JSON = new_event.serialize()
    response_JSON = jsonify(event=new_event_JSON)
    
    return (response_JSON, 201)


@api_events.route('/api/events/<int:id>', methods=['PATCH'])
def update_event(id):
    '''Updates a specific event and returns JSON'''
    
    event = Event.query.get_or_404(id)
    
    event.title = request.json.get('title', event.title)
    event.description = request.json.get('description', event.description)
    event.start_time = request.json.get('start_date', event.start_time)
    event.end_time = request.json.get('end_date', event.end_time)
    event.location = request.json.get('location', event.location)
    event.bg_color = request.json.get('bg_color', event.bg_color)
    event.txt_color = request.json.get('txt_color', event.txt_color)
    event.all_day = request.json.get('all_day', event.all_day)
    
    event.creator_id = request.json.get('creator_id', event.creator_id)
    event.calendar_id = request.json.get('calendar_id', event.calendar_id)
    
    db.session.commit()
    
    event_JSON = event.serialize()
    response_JSON = jsonify(event=event_JSON)
    
    return (response_JSON)


@api_events.route('/api/events/<int:id>', methods=['DELETE'])
def delete_event(id):
    '''Deletes a specific event and returns deletion confirmation'''
    
    event = Event.query.get_or_404(id)
    
    db.session.delete(event)
    db.session.commit()
    
    response_JSON = jsonify(message='Event has been deleted')
    
    return (response_JSON)