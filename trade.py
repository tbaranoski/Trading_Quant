#https://forum.alpaca.markets/t/get-bars-vs-get-barset/8127/6 -----Reference for get_bars

from sys import api_version
import requests , json

#Helper Functions and filepaths
import alpaca_trade_api as tradeapi #addded line
#import computations.market_health as market_health #added line
#from market_health import *
import market_health
from config import *

BASE_URL = "https://paper-api.alpaca.markets"
ACCOUNT_URL = "{}/v2/account".format(BASE_URL)
ORDERS_URL = "{}/v2/orders".format(BASE_URL)
HEADERS = {'APCA-API-KEY-ID': API_KEY, 'APCA-API-SECRET-KEY': SECRET_KEY}


def get_account(): 
    r = requests.get(ACCOUNT_URL, headers = HEADERS)

    return json.loads(r.content)

def create_order(symbol, qty, side, type, time_in_force):

    data = {
            "symbol": symbol,
            "qty": qty,
            "side": side,
            "type": type,
            "time_in_force": time_in_force
    }

    r = requests.post(ORDERS_URL, json=data ,headers = HEADERS)

    return json.loads(r.content)

def get_orders():
    r = requests.get(ORDERS_URL,headers=HEADERS)
    return json.loads(r.content)


def main():

    #Creat REST object by pasing API KEYS
    api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')
    #account = api.get_account()
    #print (account)


    #print ("test!!!")
    #orders = get_orders()
    #print(orders)

    #print ("New TEST: \n\n\n")
    distribution_array_indexes = market_health.get_distribution_health(api)
    market_health.get_ema_health(api)

    
main()