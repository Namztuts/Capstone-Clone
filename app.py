from flask import Flask, render_template, redirect, request, session, g, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Event, Calendar, create_user, add_to_db
from forms import RegisterForm, LoginForm, EventForm, CalendarForm, EditUserForm
from datetime import datetime
from api.user_routes import api_users
from api.event_routes import api_events
from api.calendar_routes import api_calendars
from dotenv import load_dotenv
import os

load_dotenv()
SECRET_KEY = os.environ.get('SECRET_KEY')
SUPABASE_URL = os.environ.get("SUPABASE_URL", 'postgresql:///calendar') # to check if the URL is being loaded

app = Flask(__name__)
app.register_blueprint(api_users) #registering the API blueprint
app.register_blueprint(api_events)
app.register_blueprint(api_calendars)

app.config['SQLALCHEMY_DATABASE_URI'] = SUPABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = SECRET_KEY
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

CURR_USER_KEY = "curr_user"

# app.app_context().push() | NOTE: updated the connect_db() method which allowed us to connect to Supabase
connect_db(app)

toolbar = DebugToolbarExtension(app)


@app.before_request
def add_user_to_g():
    '''If we're logged in, add current user to Flask global (g)'''

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id

def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/')
def index():
    return redirect('/login')

############################################
#       REGISTER/LOGIN/LOGOUT ROUTES       #
############################################

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    '''Form for creating a new User'''
    
    form = RegisterForm()
    
    if form.validate_on_submit():
        new_user = create_user(form) #method for pulling the data from the form and creating a new user | also adds to db
        
        if new_user:
            do_login(new_user)
            flash('Your account has been successfully created!', 'success')
            
            return redirect('/')
        else:
            form.email.errors.append('Email already exists. Please register with another')
            
        

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    '''Login form for User login'''
    
    form = LoginForm()
    
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        
        auth_user = User.authenticate(email, password)#NOTE: logging in seems to be working | show login home page for user specific
        
        if auth_user:
            do_login(auth_user)
            flash(f'Welcome back, {auth_user.f_name}!', 'primary')
            
            return redirect(f'/user/{auth_user.id}')
        else:
            form.email.errors = ['Invalid email/password'] #NOTE: add a unique error for both invalid Email and Password
    
    return render_template('login.html', form=form)


@app.route('/logout', methods=['POST']) #best practice is to make this a POST request due to 'pre-fetching' | some browsers pre fetch all get requests
def logout_user():
    '''Logs out User from session'''
    
    do_logout()
    flash('Successfully logged out. See ya soon!', 'danger')
    
    return redirect('/')

#####################################
#            USER ROUTES            #
#####################################

@app.route('/user/<int:user_id>')
def user_home(user_id):
    '''Shows homepage for User'''
    
    if g.user is None or g.user.id != user_id:
            flash("You are not unauthorized to access this user", "danger")
            return redirect(f'/user/{g.user.id}')
        
    user = User.query.get_or_404(user_id)
    #sorting the events by start time and are in the future
    events = (Event.query
          .filter(Event.creator_id == user_id, Event.start_time >= datetime.now())
          .order_by(Event.start_time)
          .limit(5)
          .all())
    calendars = Calendar.query.filter(Calendar.owner_id == user_id).all()
    
    return render_template ('user/user_home.html', user=user, events=events, calendars=calendars)
        

@app.route('/user/<int:user_id>/edit', methods=["GET", "POST"])
def user_edit(user_id):
    
    if g.user is None or g.user.id != user_id:
            flash("You are not unauthorized to access this user", "danger")
            return redirect(f'/user/{g.user.id}')
    
    user = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user)
    
    if form.validate_on_submit():
        auth_user = User.authenticate(user.email, form.password.data)
        
        if auth_user:
            user.email = form.email.data
            db.session.commit()
            
            flash(f'Your profile has been updated.', 'success')
            return redirect(f"/user/{user.id}")
        
        else:
            flash(f'Invalid password. No changes have been made.', 'danger')
            
        return redirect('/')
    
    return render_template('user/user_edit.html', form=form, user=user)

@app.route('/user/<int:user_id>/delete', methods=["GET", "POST"])
def user_delete(user_id):
    '''Delete a user'''
    
    user = User.query.get_or_404(user_id)
    
    if g.user is None or g.user.id != user.id:
            flash("You are not unauthorized to access this user", "danger")
            return redirect(f'/user/{user.id}')
    
    else:
        db.session.delete(user)
        db.session.commit()
        flash('User has been deleted', 'danger')
        
        return redirect("/login")

######################################
#            EVENT ROUTES            #
######################################

@app.route('/event/create', methods=["GET", "POST"])
def event_new():
    '''Create a new Event'''
    #NOTE: added this functionality to calendar/show
    form = EventForm()
    calendars = [(cal.id, cal.name) for cal in Calendar.query.filter(Calendar.owner_id == g.user.id)] #getting a list of tuples with code and name of department
    #first value in the tuple is the value that gets extracted with form.calendar_id.data
    form.calendar_id.choices = calendars
    
    if form.validate_on_submit():
        
        title = form.title.data
        description = form.description.data
        start_time = form.start_time.data
        end_time = form.end_time.data
        all_day = form.all_day.data
        location = form.location.data
    
        calendar_id = form.calendar_id.data
        creator_id = g.user.id
    
        new_event = Event(title=title, description=description, start_time=start_time, end_time=end_time, all_day=all_day, location=location,
                          calendar_id=calendar_id, creator_id=creator_id)
        
        if new_event:
            add_to_db(new_event)
            flash('New Event created!', 'success')
            return redirect(f'/user/{g.user.id}')
        else:
            form.email.errors.append('Error with creating event?!') #NOTE: add appropriate error
            
    return render_template ('event/event_new.html', form=form)

@app.route('/event/<int:event_id>/edit', methods=["GET", "POST"])
def event_edit(event_id):
    '''Edit a specific Calendar'''
    
    event = Event.query.get_or_404(event_id)
    form = EventForm(obj=event)
    
    if g.user is None or g.user.id != event.creator_id:
            flash("You are not unauthorized to access this user", "danger")
            return redirect(f'/user/{g.user.id}')
    
    if form.validate_on_submit():
        event.title = form.title.data
        event.description = form.description.data
        event.start_time = form.start_time.data
        event.end_time = form.end_time.data
        event.all_day = form.all_day.data
        event.location = form.location.data

        db.session.commit()

        return redirect(f"/user/{event.creator_id}")

    return render_template("event/event_edit.html", form=form, event=event)

@app.route('/event/<int:event_id>/delete', methods=["GET", "POST"])
def event_delete(event_id):
    '''Delete an event'''
    
    event = Event.query.get_or_404(event_id)
    
    if g.user is None or g.user.id != event.creator_id:
            flash("You are not unauthorized to access this event", "danger")
            return redirect(f'/user/{g.user.id}')
    
    else:
        db.session.delete(event)
        db.session.commit()
        flash('Event has been deleted', 'danger')
        
        return redirect(f"/user/{g.user.id}")


#########################################
#            CALENDAR ROUTES            #
#########################################

@app.route('/user/<int:user_id>/calendar/new', methods=["GET", "POST"])
def calendar_new(user_id):
    '''Create a new Calendar'''
    
    form = CalendarForm()
    
    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        is_public = form.is_public.data
        owner_id = user_id
    
        new_calendar = Calendar(name=name, description=description, is_public=is_public, owner_id=owner_id)
        
        if new_calendar:
            add_to_db(new_calendar)
            flash('New Calendar created!', 'success')
            return redirect(f'/user/{user_id}')
        else:
            form.email.errors.append('Error with creating calendar?!') #NOTE: add appropriate error
            
    return render_template ('calendar/calendar_new.html', form=form)


@app.route('/user/<int:user_id>/calendar/<int:cal_id>/edit', methods=["GET", "POST"])
def calendar_edit(user_id, cal_id):
    '''Edit a specific Calendar'''
    
    if g.user is None or g.user.id != user_id:
            flash("You are not unauthorized to access this user", "danger")
            return redirect(f'/user/{g.user.id}')
    
    calendar = Calendar.query.get_or_404(cal_id)
    form = CalendarForm(obj=calendar)
    
    if form.validate_on_submit():
        calendar.name = form.name.data
        calendar.description = form.description.data
        calendar.is_public = form.is_public.data

        db.session.commit()

        return redirect(f"/user/{user_id}")

    return render_template("calendar/calendar_edit.html", form=form, calendar=calendar)


@app.route('/user/<int:user_id>/calendar/<int:cal_id>', methods=["GET", "POST"])
def calendar_show(user_id, cal_id):
    '''Show user Calendar and Events'''
    #NOTE: need to test verification for calendar and also so user can only view their calendars
    if g.user is None or g.user.id != user_id:
            flash("You are not unauthorized to access this user", "danger")
            return redirect('/login')

    form = EventForm()
    calendar = Calendar.query.get_or_404(cal_id)
    
    if form.validate_on_submit():
        
        title = form.title.data
        description = form.description.data
        start_time = form.start_time.data
        end_time = form.end_time.data
        location = form.location.data
        bg_color = form.bg_color.data
        txt_color = form.txt_color.data
        all_day = form.all_day.data
    
        calendar_id = cal_id
        creator_id = user_id
    
        new_event = Event(title=title, description=description, start_time=start_time, end_time=end_time, location=location, bg_color=bg_color, txt_color=txt_color,
                        all_day=all_day, calendar_id=calendar_id, creator_id=creator_id)
        
        if new_event:
            add_to_db(new_event)
            return redirect(f'/user/{user_id}/calendar/{cal_id}')
        else:
            form.email.errors.append('Error with creating event?!')
    
    return render_template('calendar/calendar_show.html', calendar=calendar, form=form)

@app.route('/calendar/<int:cal_id>/delete', methods=["GET", "POST"])
def calendar_delete(cal_id):
    '''Delete a calendar'''
    
    calendar = Calendar.query.get_or_404(cal_id)
    
    if g.user is None or g.user.id != calendar.owner_id:
            flash("You are not unauthorized to access this calendar", "danger")
            return redirect(f'/user/{g.user.id}')
    
    else:
        db.session.delete(calendar)
        db.session.commit()
        flash('Calendar has been deleted', 'danger')
        
        return redirect(f"/user/{g.user.id}")
