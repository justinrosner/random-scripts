#!/usr/bin/env python3

'''
This is loosely based off of the prices.py file found here:
https://github.com/LukasJoswiak/blog-code/blob/master/2020/tracking-commodity-prices-ledger/prices.py

The main difference is that I needed to change the API (and some of the logic)
since it wouldn't account for Canadian commodities
'''

from datetime import datetime
import yfinance as yf
import sys

# Symbol definition
SYMBOLS = ['BRK-B', 'AAPL', 'BLK', 'DIS', 'MSFT', 'TD.TO', 'RY.TO', 'ENB.TO',
           'VFV.TO', 'XBAL.TO', 'XGRO.TO']
USD_SYMBOLS = ['BRK-B', 'AAPL', 'BLK', 'DIS', 'MSFT']
TICKER_TO_LEDGER_NAME = {'BRK-B': 'BRKB', 'AAPL': 'AAPL', 'BLK': 'BLK',
                         'DIS': 'DIS', 'MSFT': 'MSFT', 'TD.TO': 'TD',
                         'RY.TO': 'RY', 'ENB.TO': 'ENB', 'VFV.TO': 'VFV',
                         'XBAL.TO': 'XBAL', 'XGRO.TO': 'XGRO'}
PRICES_FILE = 'prices.db'

def query_data(symbol):
    # Pull price data
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="1d")
    return hist


def output(symbol, prices):
    data = query_data(symbol)

    try:
      adjusted_close = data.Close[0]
      date = str(data.axes[0][0])

      # Convert date string to date object.
      date = datetime.strptime(date, '%Y-%m-%d 00:00:00-05:00').date()

      # Look through existing entries to make sure a price for this date doesn't
      # already exist.
      for price in prices:
        if len(price) != 4:
            continue

        # Grab date and symbol from existing entry.
        parsed_date = datetime.strptime(price[1], '%Y/%m/%d').date()
        parsed_symbol = price[2]

        if parsed_symbol == symbol and parsed_date == date:
          print(f'existing price found for {symbol} on {date}: {price[3]} '
                 '(${adjusted_close})')
          return None

      out = ''
      # If we are dealing with a USD symbol we need to output a slightly different
      # format for ledger to consume
      if (symbol in USD_SYMBOLS):
        out = f'P {date} {TICKER_TO_LEDGER_NAME[symbol]} {adjusted_close} $USD\n'
      else:
        out = f'P {date} {TICKER_TO_LEDGER_NAME[symbol]} ${adjusted_close}\n'

      return out
    except:
        print(f'data not found in expected format for {symbol}, exiting...')
        sys.exit(0)



if __name__ == '__main__':
    datetime = datetime.now()
    # For logging purposes
    print(datetime)

    with open(PRICES_FILE, 'r') as f:
        prices = f.readlines()
    prices = [x.strip().split() for x in prices]

    lines = []
    for symbol in SYMBOLS:
        line = output(symbol, prices)
        if line:
            lines += [line]

    if len(lines) > 0:
        with open(PRICES_FILE, 'a') as f:
            f.write('\n')
            for line in lines:
                print(f'writing {line.strip()}')
                f.write(line)
