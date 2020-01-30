# Chat App

Simple chat application using flask-socketio

## Requirements

- Python 3.3+
- PostgreSQL 11+
- Redis 5+

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

Make sure postgres and redis are running.

Set environment variables (use example.env as a template):

```
cp example.env .env
```

Source environment variables

```
. .env
```

Run celery worker (task queue)

```
celery worker -A chat.tasks --loglevel INFO
```

Run application:

```
gunicorn -c "python:config.gunicorn" "chat:create_app()"
```

App should be running on port 8000 :)