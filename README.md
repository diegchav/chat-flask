# Chat App

Simple chat application using flask-socketio

## Requirements

- Python 3.7.5+
- PostgreSQL 11.5+

## Setup project

Clone repo:

```
git clone https://github.com/diegchav/chat-flask.git
cd chat-flask
```

Create virtualenv and activate:

```
python3 -m venv venv
. venv/bin/activate
```

Install dependencies:

```
pip install -r requirements.txt
```

## Run project

Set environment variables (use example.env as a template):

```
cp example.env .env
```

SECRET_KEY can have any value

Create db schemas:

```
python -c "from chat import app; app.db.create_all()"
```

Run application:

```
python chat/app.py
```

App should be running on port 5000 :)
