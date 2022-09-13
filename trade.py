#https://forum.alpaca.markets/t/get-bars-vs-get-barset/8127/6 -----Reference for get_bars

from pickle import NONE
from sys import api_version
import requests , json

#Helper Functions and filepaths
import alpaca_trade_api as tradeapi #addded line
#import computations.market_health as market_health #added line
#from market_health import *
import market_health
from config import *

#imports for alpha_vantage package
from alpha_vantage.alpha_vantage.timeseries import TimeSeries
from alpha_vantage.alpha_vantage.techindicators import TechIndicators
import matplotlib.pyplot as plt

#test for alpha_vantage
#def get_ema(self, symbol, interval='daily', time_period=20, series_type='close'):
#ti = TechIndicators(key= API_KEY, output_format='pandas')
#data, meta_data = ti.get_ema(symbol='MSFT', interval='daily', time_period=21)
#data.plot()
#plt.title('21 EMA indicator for  MSFT stock (DAILY)')
#plt.show()

#ts = TimeSeries(key='YOUR_API_KEY', output_format='pandas')
#data, meta_data = ts.get_intraday(symbol='MSFT',interval='1min', outputsize='full')
#data['4. close'].plot()
#plt.title('Intraday Times Series for the MSFT stock (1 min)')
#plt.show()
##############################################################################
BASE_URL = "https://paper-api.alpaca.markets"
ACCOUNT_URL = "{}/v2/account".format(BASE_URL)
ORDERS_URL = "{}/v2/orders".format(BASE_URL)
HEADERS = {'APCA-API-KEY-ID': API_KEY, 'APCA-API-SECRET-KEY': SECRET_KEY}


#Create stock class to store the key data that will be used in the trading strategy.
#This will allow us to choose different strategies to use for different stocks
class Stock:
    def __init__(self, name, current_price_estimate = NONE, EMA_21 = None, EMA_9 = None, distribution_Short_len = None, distribution_Long_len = None, strategy = None):
        self.name = name
        self.current_price_estimate = current_price_estimate        
        self.EMA_21 = EMA_21
        self.EMA_9 = EMA_9
        self.distribution_Short_len = distribution_Short_len
        self.distribution_Long_len = distribution_Long_len
        self.strategy = strategy

        #Calculate EMA score
        #IF Over both short and long EMA then score is 2/2 BULLISH

        #Try Except block in case default value of None is used
        try:
            if(self.current_price_estimate > self.EMA_21) and (self.current_price_estimate > self.EMA_9):
                self.EMA_SCORE = 2

            #If Over 21 EMA, but below 9 EMA then score is 1/2 BULLISH
            if(self.current_price_estimate > self.EMA_21) and (self.current_price_estimate < self.EMA_9):
                self.EMA_SCORE= 1

            #If Under 21 EMA then SCORE 0 then score is 0/2 BULLISH
            if(self.current_price_estimate < self.EMA_21):
                self.EMA_SCORE = 0
        except: 
            print("block ran..!!!")
            self.EMA_SCORE = None

############################################################################################################
############################################################################################################

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
    SPY_TEST = market_health.get_ema_health(api)

    print("MAIN FUNCTION: SPY PRINTING: ", SPY_TEST[7])

    #Test making SPY object
    SPY_object = Stock('SPY')


main()