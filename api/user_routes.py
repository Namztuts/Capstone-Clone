from flask import Flask, request, jsonify, Blueprint
from models import connect_db, db, User

app = Flask(__name__)
api_users= Blueprint('api_users', __name__) #creating the API blueprint

app.config["SECRET_KEY"] = "oh-so-secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///calendar"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.app_context().push()
connect_db(app)

@api_users.route('/api')
def index():
    '''API landing page'''
    return {"message": "Welcome to the calendar API"}

#########################################
#              USER ROUTES              #
#########################################

@api_users.route('/api/users')
def list_users():
    '''Returns JSON for all users'''
    
    users = User.query.all()
    users_JSON = [user.serialize() for user in users]
    response_JSON = jsonify(users=users_JSON)
    
    return (response_JSON)


@api_users.route('/api/users/<int:id>')
def get_user(id):
    '''Returns JSON for a specific user'''
    
    user = User.query.get_or_404(id)
    user_JSON = user.serialize()
    response_JSON = jsonify(user=user_JSON)
    
    return (response_JSON)


@api_users.route('/api/users', methods=['POST'])
def create_user():
    '''Creates a new user and return JSON'''
    
    email = request.json['email']
    password = request.json['password'] #NOTE: gonna be grabbing the already serialized data from the form
    f_name = request.json['f_name']
    l_name = request.json['l_name']
    new_user = User(email=email, password=password, f_name=f_name, l_name=l_name)
    
    db.session.add(new_user)
    db.session.commit()
    
    new_user_JSON = new_user.serialize()
    response_JSON = jsonify(user=new_user_JSON)
    
    return (response_JSON, 201)


@api_users.route('/api/users/<int:id>', methods=['PATCH'])
def update_user(id):
    '''Updates a specific user and returns JSON'''
    
    user = User.query.get_or_404(id)
    
    user.email = request.json.get('email', user.email)
    user.password = request.json.get('password', user.password)
    user.f_name = request.json.get('f_name', user.f_name)
    user.l_name = request.json.get('l_name', user.l_name)
    #NOTE: data/time user was last updated?
    
    db.session.commit()
    
    user_JSON = user.serialize()
    response_JSON = jsonify(user=user_JSON)
    
    return (response_JSON)


@api_users.route('/api/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    '''Deletes a specific user and returns deletion confirmation'''
    
    user = User.query.get_or_404(id)
    
    db.session.delete(user)
    db.session.commit()
    
    response_JSON = jsonify(message='User has been deleted')
    
    return (response_JSON)