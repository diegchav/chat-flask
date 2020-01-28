from datetime import datetime

from . import db, ma, moment

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)

    def __init__(self, username, password):
        self.username = username.strip().lower()
        self.password = password

    def __repr__(self):
        return '<User {}>'.format(self.username)


class UserSchema(ma.ModelSchema):
    class Meta:
        fields = ('id', 'username')


class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(), nullable=False)
    timestamp = db.Column(db.DateTime(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref='messages')

    def __init__(self, message, user_id):
        self.message = message.strip()
        self.user_id = user_id
        self.timestamp = datetime.utcnow()

    def __repr__(self):
        return '<Message {}>'.format(self.message)


class MessageSchema(ma.ModelSchema):
    class Meta:
        model = Message

    user = ma.Pluck('UserSchema', 'username')
    timestamp = ma.Function(lambda obj: moment.create(obj.timestamp).calendar()) # Markup representation
    timestamp_raw = ma.Function(lambda obj: str(obj.timestamp)) # Raw string representation for javascript