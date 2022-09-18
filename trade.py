#https://forum.alpaca.markets/t/get-bars-vs-get-barset/8127/6 -----Reference for get_bars

from pickle import NONE
from sys import api_version
from unicodedata import name
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
import logging #for try-except blocks

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

############################################################################################################
############################################################################################################
    #Create Group Object (Parent Class) which will be used to store groups of different stocks to better performe quantitative analysis##### 
class Group:
    def __init__(self, stock_objects_array = [], name_group = None, sector = None, description = None):

        self.stock_objects_array = stock_objects_array
        self.name_group = name_group
        self.sector = sector
        self.description = description
        try:
            self.num_in_group = len(stock_objects_array)
        except:
            self.num_in_group = 0

    #Create a Group given a list of tickers
    def create_group(self, ticker_list, name_group):

        #Create Stock Object and populate group
        for name in ticker_list:    
            temp_stock_object = Stock(name) 
            self.stock_objects_array.append(temp_stock_object)

        #Name the group if name given
        try:
            self.name_group = name_group
        except:
            pass

    def print_group_names(self):

        print("\n\n Stocks in the ", self.name_group, " group are: \n")
        for stock_object in self.stock_objects_array:
            print(stock_object.name)


    def print_group_data(self):

        temp_string_ld = "Distribution ("  + str(market_health.LONG_DISTRIBUTION_NUMBER) + " Day)"
        temp_string_sd = "Distribution ("  + str(market_health.SHORT_DISTRIBUTION_NUMBER) + " Day)"

        print ('\033[1m') #Bold FONT ON
        print("Group: ", self.name_group)
        print('{:<10} {:^15} {:^20} {:^20} {:^20} {:^30}'.format("Name", "Est. Price", "21 EMA" , "9 EMA", temp_string_ld, temp_string_sd))
        print ('\033[0m') #Bold FONT OFF

        #Print Attributes For the Stock
        for temp_name in self.stock_objects_array:
            temp_name.print_attributes()



#Create stock class (Child Class) to store the key data that will be used in the trading strategy.
#This will allow us to choose different strategies to use for different stocks
class Stock(Group):
    def __init__(self, name, current_price_estimate = None, EMA_21 = None, EMA_9 = None, distribution_Short_len = None, distribution_Long_len = None, strategy = None):
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
            self.EMA_SCORE = None
    
    #Print the stock attributes
    def print_attributes(self):

        #Try to print attributes if populated
        try:
            print('{:<10} {:^15} {:^20} {:^20} {:^20} {:^30}'.format(str(self.name), str(self.current_price_estimate), round(self.EMA_21, 2), round(self.EMA_9, 2), self.distribution_Short_len, self.distribution_Long_len))

        except Exception as Argument:
            logging.exception("Error occured printing stock attributes. (Stock Attributes may not be populated)")



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
    ###################################################################
    #Modify the lists below...
    index_names_array = ['SPY', 'QQQ', 'IWM', 'IWO', 'DIA']


    #Creat REST object by pasing API KEYS
    api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')
    #account = api.get_account()
    #print (account)


    #Create Index Group
    index_group = Group()
    index_group.create_group(index_names_array, name_group = "Indexes")
    index_group.print_group_names()

    #print ("test!!!")
    #orders = get_orders()
    #print(orders)
    #print ("New TEST: \n\n\n")

    market_health.get_distribution_health(api, index_group)
    market_health.get_ema_health(api, index_group)

    #print("TEST FROM MAIN FUNCTION", index_group.stock_objects_array[3].name, index_group.stock_objects_array[3].EMA_21)

    #Test Print Object Funciton
    index_group.print_group_data()
    



    #Populate index_group


main()