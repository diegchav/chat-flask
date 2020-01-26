import functools
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from flask_moment import Moment
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

# Load environment variables from .env file
load_dotenv()

db = SQLAlchemy()

moment = Moment()

socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    moment.init_app(app)
    socketio.init_app(app)

    with app.app_context():
        from .models import User, Message

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
            user = g.user
            messages = [message.json() for message in Message.query.limit(50).all()]
            return render_template('index.html', username=user.username, messages=messages)

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

        @app.route('/logout')
        def logout():
            session.clear()
            return redirect(url_for('login'))

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

        @socketio.on('stock message')
        def handle_stock_message(stock_code):
            stock_url = 'https://stooq.com/q/l/?s={}&f=sd2t2ohlcv&h&e=csv'.format(stock_code.strip().lower())
            r = requests.get(stock_url)

            # Parse csv response
            csv_text = r.text
            csv_rows = csv_text.splitlines()
            csv_values = csv_rows[1].split(',')
            stock_symbol = csv_values[0]
            stock_close = csv_values[6]

            if is_float(stock_close):
                message_text = '{} quote is ${} per share.'.format(stock_symbol, stock_close)
                message_user = 'Bot'
                message_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                emit('message received', { 'text': message_text, 'user': message_user, 'time': message_time }, broadcast=True)

        # Create db models
        db.create_all()

        return app