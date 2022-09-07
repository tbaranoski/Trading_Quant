from alpaca_trade_api.rest import REST, TimeFrame
import datetime as dt #to get date
import config
import pytz #to get date
import math #rounding purposes

#Threading headers so that the websocket can run on its own thread
#import threading

import logging
from alpaca_trade_api.stream import Stream
from alpaca_trade_api.common import URL #not sure if needed

log = logging.getLogger(__name__)

###########################################################################
#Helper Functions taken from V2_example.py
async def print_trade(t):
    print('trade', t)


async def print_quote(q):
    print('quote', q)


async def print_trade_update(tu):
    print('trade update', tu)


async def print_crypto_trade(t):
    print('crypto trade', t)

#I added print_daily_bar()
async def print_daily_bar(db):
    print('Daily Bar for',db.get('S'), ':', db.get('c'))  
    return db.get('c') 


#END of Helper Functions
###########################################################################

def get_today_daily_bar(ticker_name):
    
    #Set up Websocket
    logging.basicConfig(level=logging.INFO)
    feed = 'iex'  # <- replace to SIP if you have PRO subscription
    stream = Stream(data_feed=feed, raw_data=True, key_id= config.API_KEY, secret_key=config.SECRET_KEY, base_url="https://paper-api.alpaca.markets")

    #Start Subscriptions
    #stream.subscribe_trade_updates(print_trade_update)
    #stream.subscribe_trades(print_trade, 'AAPL')
    #stream.subscribe_quotes(print_quote, 'IBM')
    #already_printed_boolean = False
    #print(already_printed_boolean)
   
   
    price = stream.subscribe_daily_bars(print_daily_bar, ticker_name)
    #stream.stop_ws()
    #print(already_printed_boolean)

    #If we have already got the daily_bar data then unsubscribe
    #if(already_printed_boolean == True):
        #stream.unsubscribe_daily_bars(ticker_name)

    #@stream.on_bar('MSFT')
    #async def _(bar):
        #print('bar', bar)

    #@stream.on_updated_bar('SPY')
    #async def _(bar):
        #print('updated bar', bar)

    #@stream.on_status("*")
    #async def _(status):
        #print('status', status)

    #@stream.on_luld('AAPL', 'MSFT')
    #async def _(luld):
        #print('LULD', luld)

    #stream.stop_ws()
    stream.run()
    
    return price


#if __name__ == "__main__":
    #main()
