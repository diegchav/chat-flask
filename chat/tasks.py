import os
import requests
from datetime import datetime
from flask_socketio import SocketIO

from . import make_celery
from .utils import is_float

celery = make_celery()
socketio = SocketIO(message_queue=os.environ['MESSAGE_QUEUE'])

@celery.task()
def quote_stock(stock_code):
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
    else:
        message_text = 'Invalid stock code: {}'.format(stock_code)

    message_user = 'Bot'
    message_time = str(datetime.utcnow())
    message = { 'message': message_text, 'user': message_user, 'timestamp': message_time }

    socketio.emit('message received', message, broadcast=True)