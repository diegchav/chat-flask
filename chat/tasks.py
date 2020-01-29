import requests
from datetime import datetime

from .extensions import celery
from .utils import is_float

@celery.task()
def quote_stock(stock_code):
    print('quoting stock: ' + stock_code)
    stock_url = 'https://stooq.com/q/l/?s={}&f=sd2t2ohlcv&h&e=csv'.format(stock_code.strip().lower())
    r = requests.get(stock_url)

    # Parse csv response
    csv_text = r.text
    csv_rows = csv_text.splitlines()
    csv_values = csv_rows[1].split(',')
    stock_symbol = csv_values[0]
    stock_close = csv_values[6]

    if is_float(stock_close):
        message = '{} quote is ${} per share.'.format(stock_symbol, stock_close)
        print(message)
    else:
        print('Invalid stock code: {}'.format(stock_code))