from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateTimeField, BooleanField, SelectField
from wtforms.validators import InputRequired, Email, Length, ValidationError

BG_COLORS = [
    ('#dc2127', 'Alizarin Crimson'),
    ('#51b749', 'Apple'),
    ('#5484ed', 'Cornflower Blue'),
    ('#fbd75b', 'Dandelion'),
    ('#ffb878', 'Mac n Cheese'),
    ('#dbadff', 'Mauve'),
    ('#a4bdfc', 'Melrose'),
    ('#e1e1e1', 'Mercury'),
    ('#7ae7bf', 'Riptide'),
    ('#46d6db', 'Turquoise'),
    ('#ff887c', 'Vivid Tangerine')
]
TXT_COLORS =[
    ('#ffffff', 'White'),
    ('#808080', 'Gray'),
    ('#000000', 'Black'),
]

class RegisterForm(FlaskForm):
    '''Form for registering a user'''

    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    f_name = StringField('First Name', validators=[InputRequired()])
    l_name = StringField('Last Name', validators=[InputRequired()])
    
class LoginForm(FlaskForm):
    '''Form for logging in'''

    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    
class EventForm(FlaskForm):
    '''Form for creating events'''
    
    title = StringField('Title', validators=[InputRequired()])
    description = StringField('Description', validators=[InputRequired()])
    start_time = DateTimeField('Start Time', format='%Y-%m-%dT%H:%M', validators=[InputRequired()])
    end_time = DateTimeField('End Time', format='%Y-%m-%dT%H:%M', validators=[InputRequired()])
    location = StringField('Location')
    bg_color = SelectField('Background Color', choices = BG_COLORS, default='#e1e1e1')
    txt_color = SelectField('Text Color', choices = TXT_COLORS, default='#000000')
    all_day = BooleanField('All Day')
        
class CalendarForm(FlaskForm):
    '''Form for creating calendars'''
    
    name = StringField('Name', validators=[InputRequired()])
    description = StringField('Description', validators=[InputRequired()])
    is_public = BooleanField('Public?')

class EditUserForm(FlaskForm):
    '''Form for editing a user'''

    email = StringField('E-mail', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    