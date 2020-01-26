import json
import requests
from datetime import datetime
from functools import wraps
from flask import (
    Blueprint, abort, g, jsonify, redirect, render_template, session, url_for
)
from werkzeug.exceptions import Unauthorized
from flask_socketio import emit

from . import db, moment, socketio
from .models import Message, MessageSchema, User

bp = Blueprint('chat', __name__)

# Model schemas
message_schema = MessageSchema()
messages_schema = MessageSchema(many=True)

# Error handlers
@bp.errorhandler(Unauthorized)
def handle_unauthorized(e):
    response = e.get_response()
    response.data = json.dumps({
        'error': e.name,
        'code': e.code
    })
    response.content_type = 'application/json'

    return response

# Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return f(*args, **kwargs)

    return decorated_function

def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            abort(401)

        return f(*args, **kwargs)

    return decorated_function

@bp.route('/')
@login_required
def index():
    """Home page."""
    user = g.user
    messages = Message.query.limit(50).all()
    messages = messages_schema.dump(messages)

    return render_template('index.html', username=user.username, messages=messages)

### WebSocket events ###
@socketio.on('message')
def handle_message(message):
    user_id = session.get('user_id')
    user = User.query.filter_by(id=user_id).first()
    if user:
        new_message = Message(message=message, user_id=user.id)
        db.session.add(new_message)
        db.session.commit()

        message_json = message_schema.dump(new_message)
        # Just keep raw string representation for using it with javascript
        message_json['timestamp'] = message_json['timestamp_raw']
        message_json.pop('timestamp_raw')

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