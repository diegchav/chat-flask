import functools
import os
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from flask_moment import Moment
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

moment = Moment(app)

socketio = SocketIO(app)

### Models ###
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)

    def __init__(self, username, password):
        self.username = username.strip().lower()
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username

class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref='messages')

    def __init__(self, message, user_id):
        self.message = message.strip()
        self.user_id = user_id
        self.timestamp = datetime.now()

    def __repr__(self):
        return '<Message %r>' % self.message

    def json(self):
        message_json = {
            'text': self.message,
            'user': self.user.username,
            'time': moment.create(self.timestamp).calendar()
        }
        print(message_json)
        return message_json

### Routes ###
@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        user = User.query.filter_by(id=user_id).first()
        g.user = user

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('login'))

        return view(**kwargs)

    return wrapped_view

@app.route('/')
@login_required
def index():
    """Home page."""
    messages = [message.json() for message in Message.query.limit(50).all()]
    return render_template('index.html', messages=messages)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session.clear()
            session['user_id'] = user.id

            return redirect(url_for('index'))
        else:
            error = 'Invalid username or password'

        flash(error)

    if g.user:
        return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm-password']
        error = None

        if not username:
            error = 'Username is required'
        elif not password or not confirm_password:
            error = 'Password is required'
        elif password != confirm_password:
            error = 'Password and Confirm Password don\'t match'
        else:
            existing_user = User.query.filter_by(username=username).first()
            # Don't enumerate usernames
            if existing_user is None:
                new_user = User(username=username, password=generate_password_hash(password))
                db.session.add(new_user)
                db.session.commit()
            
            return redirect(url_for('login'))

        flash(error)

    if g.user:
        return redirect(url_for('index'))

    return render_template('register.html')

### WebSocket events ###
@socketio.on('message')
def handle_message(message):
    user_id = session.get('user_id')
    user = User.query.filter_by(id=user_id).first()
    if user:
        new_message = Message(message=message, user_id=user.id)
        db.session.add(new_message)
        db.session.commit()
        
        message_json = new_message.json()
        message_json['time'] = new_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        emit('message received', message_json, broadcast=True)

if __name__ == "__main__":
    socketio.run(app)