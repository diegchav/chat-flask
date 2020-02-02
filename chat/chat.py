from flask import Blueprint, render_template
from flask_login import current_user, login_required
from flask_socketio import emit

from .constants import NAMESPACE
from .extensions import db, socketio
from .models import Message, MessageSchema

bp = Blueprint('chat', __name__)

# Model schemas
message_schema = MessageSchema()
messages_schema = MessageSchema(many=True)

@bp.route('/')
@login_required
def index():
    """Home page."""
    # Get 50 newest messages
    messages = Message.query.order_by(Message.timestamp.desc()).limit(50).all()
    messages = messages_schema.dump(messages)
    messages.reverse()

    return render_template('index.html', messages=messages)

### WebSocket events ###
@socketio.on('message', namespace=NAMESPACE)
def handle_message(message):
    if current_user.is_authenticated:
        user = current_user
        new_message = Message(message=message, user_id=user.id)
        db.session.add(new_message)
        db.session.commit()

        message_json = message_schema.dump(new_message)
        # Just keep raw string representation for using it with javascript
        message_json['timestamp'] = message_json['timestamp_raw']
        message_json.pop('timestamp_raw')

        emit('message received', message_json, broadcast=True)

@socketio.on('stock message', namespace=NAMESPACE)
def handle_stock_message(message):
    from .tasks import quote_stock
    quote_stock.delay(message, NAMESPACE)