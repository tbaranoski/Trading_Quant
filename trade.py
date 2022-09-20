#https://forum.alpaca.markets/t/get-bars-vs-get-barset/8127/6 -----Reference for get_bars

from ast import And
from email.policy import default
from pickle import NONE
from statistics import mode
from sys import api_version
from unicodedata import name
import requests , json

#Helper Functions and filepaths
import alpaca_trade_api as tradeapi #addded line
import pytz #to get date
from alpaca_trade_api.rest import REST, TimeFrame
import time
#import computations.market_health as market_health #added line
#from market_health import *
import market_health
from config import *
import logging #for try-except blocks
from enum import Enum

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

#Set log level to INFO to debug (WARNING is default)
logging.basicConfig(level=logging.WARNING)

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
        print("Group:", self.name_group)
        print('{:<10} {:^15} {:^15} {:^20} {:^20} {:^20} {:^30}'.format("Name", "Trend", "Est. Price", "21 EMA" , "9 EMA", temp_string_ld, temp_string_sd))
        print ('\033[0m') #Bold FONT OFF

        #Print Attributes For the Stock
        for temp_name in self.stock_objects_array:
            temp_name.print_attributes()

#Create stock class (Child Class) to store the key data that will be used in the trading strategy.
#This will allow us to choose different strategies to use for different stocks
class Stock(Group):
    def __init__(self, name, current_price_estimate = None, EMA_21 = None, EMA_9 = None, distribution_Short_len = None, distribution_Long_len = None, current_trend = None, strategy = None, data_temp = [], current_timeframe_string = "Day"):
        self.name = name
        self.current_price_estimate = current_price_estimate        
        self.EMA_21 = EMA_21
        self.EMA_9 = EMA_9
        self.distribution_Short_len = distribution_Short_len
        self.distribution_Long_len = distribution_Long_len
        self.strategy = strategy
        self.dataset = data_temp
        self.current_timeframe_string = current_timeframe_string 
        
        #If a trend starting value is provided, create object with it
        if(current_trend != None):

            try:
                logging.info("Starting State for Trend provided")
                self.trend = Trend(state = current_trend)

            except:
                self.trend = Trend() #create DEFAULT trend object since custom wont work
                logging.error("ERROR loading current_trend attribute to trend object (child class). Default trend object created.")

        #If no trend starting value is passed, create default Trend object
        else:
            logging.info("NO Starting State for Trend provided, DEFAULT USED")
            self.trend = Trend() #create DEFAULT trend object


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
            print('{:<10} {:^15} {:^15} {:^20} {:^20} {:^20} {:^30}'.format(str(self.name), str(self.trend.print_trend_D()), str(self.current_price_estimate), round(self.EMA_21, 2), round(self.EMA_9, 2), self.distribution_Long_len, self.distribution_Short_len))

        except Exception as Argument:
            logging.exception("Error occured printing stock attributes. (Stock Attributes may not be populated)")


    def print_trend(self):
        print("The trend for: ",self.name, " is ", self.trend)

    ##################################################################################################################################
    #Fucntion Analyzes data looking for Higher Highs, Higher Lows, Lower Lows and Lower Highs with Price Action
    def determine_ititial_trend(self):
        ############################################################################################################################
        ############################################################################################################################
        ####   CONSTRUCTION START   ####
        NUM_CANDLES = len(self.dataset)
        SKIP_INCREMENT = 2 #Every other candle
        MODE = None #True = Looking for next relative High. False = Looking for next relative Low
        #last_high = None
        #last_low = None

        #new_high = None
        #new_low = None

        #Start trend itteration at the first candle
        i = 0 + SKIP_INCREMENT
        while(i < NUM_CANDLES):
            
            #Edge Case: Evaluating first candle, determine initial direction and set MODE
            if(i == SKIP_INCREMENT):

                #direction up initially
                if(self.dataset[i] > self.dataset[i - SKIP_INCREMENT]):
                    MODE = True
                    self.trend.last_high = self.dataset[0]

                #direction down initially
                else:
                    MODE = False
                    self.trend.last_low = self.dataset[0]
            ###end endge case if

            #Determine if we are looking for Relative High or Relative Low
            #Looking for High, if current candle is higher mark as new high
            array = self.find_pivot(i, MODE, SKIP_INCREMENT)
            i = array[0]
            self.process_pivot(array[1], MODE)
            
            #Negate the MODE
            MODE = not MODE

            #Update the Trend State Machine
            self.trend.update_state()


            i = i + SKIP_INCREMENT
        #### END OF WHILE

    ############################################################################################################################
    #Helper Function to store the pivot found in appropriate place as well as update counters
    def process_pivot(self, pivot, mode):
        
        #Process New High
        if(mode == True):

            #Compare to last High
            #If Higher add to higher high, reset lower high
            if(pivot > self.trend.last_high):
                self.trend.higher_high_count = self.trend.higher_high_count + 1
                self.trend.lower_high_count = 0
            
            #If Lower reset higher high, add to lower high
            else:
                self.trend.higher_high_count = 0
                self.trend.lower_high_count = self.trend.lower_high_count + 1

            #Save pivot
            self.trend.last_high = pivot
        
        #############################################################################
        #Process Low
        elif(mode == False):

            #Compare to last Low
            #If lower add to lower low count and reset higher low count
            if(pivot < self.trend.last_low):
                self.trend.lower_low_count = self.trend.lower_low_count + 1
                self.trend.higher_low_count = 0
            
            #If higher low reset lower low count and increment higher low
            else:
                self.trend.lower_low_count = 0
                self.trend.higher_low_count = self.trend.higher_low_count + 1

            #Save pivot
            self.trend.last_low = pivot
            
    ####end of function
    ############################################################################################################################

    #Function Determines if relative high or low was spotted
    #Leave Function when Found
    def find_pivot(self, i, mode, SKIP_INCREMENT):
        up_counter = 0
        down_counter = 0
        return_index = None #Returns the index where we left off

        NUM_CANDLES = len(self.dataset)
        HIGH_CONFIRM = 3
        LOW_CONFIRM = 3

        #Initial setup of "markers"
        #Determine to set temporary new_high or new_low value based on the mode
        if(mode == True):
            self.trend.new_high = self.dataset[i]
        elif(mode == False):
            self.trend.new_low = self.dataset[i]


        ##################################################################################
        ##################################################################################
        #Increment by one candle at a time
        while(i < NUM_CANDLES):

            #Looking for HIGH
            if(mode == True):

                #If new temp_high was made
                if(self.dataset[i] > self.trend.new_high):
                    self.trend.new_high = self.dataset[i]
                    up_counter = 0 #reset counter since new highs being made

                #HIGH might be in place
                else:
                    up_counter = up_counter + 1

                #Check counter to see if HIGH can be officially Confirmed
                #confirmed
                if(up_counter == HIGH_CONFIRM):
                    break
            
            ################################################################
            #Looking for LOW
            elif(mode == False):
                  
                #If new temp_low was made
                if(self.dataset[i] < self.trend.new_low):
                    self.trend.new_low = self.dataset[i]
                    down_counter = 0 #reset counter since new highs being made

                #Low might be in place
                else:
                    down_counter = down_counter + 1

                #Check counter to see if Low can be officially Confirmed
                #confirmed
                if(down_counter == LOW_CONFIRM):
                    break
            
            i = i + 1 #increment the counter
        #end while

        #Send pivot index and Price back
        if(mode == True):
            pivot = self.trend.new_high
            return_index = i - HIGH_CONFIRM

        elif(mode == False):
            pivot = self.trend.new_low
            return_index = i - LOW_CONFIRM
        
        return [return_index, pivot]

############################################################################################################
############################################################################################################
#1: confirmed_uptrend: Confirmed Uptrend
#2: possible_uptrend_reversal: Trend Might Reverse from Uptrend to Downtrend
#3: confirmed_downtrend: Confirmed Downtrend
#4: possible_downtrend_reversal: Trend Might Reverse from Downtrned to Uptrend
#5: volitility_contraction: The Market is going Sideways and Contracting
#6: volitility_expansion: Volitility is Expanding
#7: The initial state

class trend_state(Enum):
    confirmed_uptrend = 1
    possible_uptrend_reversal = 2
    confirmed_downtrend = 3
    possible_downtrend_reversal = 4
    volitility_contraction = 5
    volitility_expansion = 6
    starting_state = 7
    debug = 8 #Used for troubleshooting
    
############################################################################################################
############################################################################################################

#Tracks the trend in a specific timeframe via states. See readme.md for picture dictating state machine and basic logic.
#See trend_state(Enum) above for additional info

class Trend(Stock):

    def __init__(self, trend_child_Week = trend_state.starting_state, current_trend = trend_state.starting_state, trend_hour = trend_state.starting_state, trend_30min = trend_state.starting_state, trend_15min = trend_state.starting_state, trend_5min = trend_state.starting_state, trend_1min = trend_state.starting_state, higher_high_counter = 0, lower_low_counter = 0, higher_low_counter = 0, lower_high_counter = 0):
        
        #Trend Attributes for Different TimeFrames
        self.trend_child_Week = trend_child_Week
        self.trend_child_Day = current_trend #default state if no current_trend is passed in. (Will be used 99% of time). Note: Daily timeframe
        self.trend_child_Hour = trend_hour
        self.trend_child_30min = trend_30min
        self.trend_child_15min = trend_15min
        self.trend_child_5min = trend_5min
        self.trend_child_1min = trend_1min

        #For Computations and Determing Trend
        self.higher_high_counter = higher_high_counter
        self.higher_low_counter = higher_low_counter
        self.lower_low_counter = lower_low_counter
        self.lower_high_counter = lower_high_counter

        #temporary trackers
        self.last_high = None
        self.last_low = None
        self.new_high = None
        self.new_low = None

    ##################################################################

    #Resets trend markers to default when computing trend for a new timeframe
    def reset_trend_markers(self):
        self.higher_high_counter = 0
        self.higher_low_counter = 0
        self.lower_low_counter = 0
        self.lower_high_counter = 0

    #Print Main Daily Trend
    def print_trend_D(self):
        return (self.trend_child_Day.name)

    ####################################################################################################
    ####################################################################################################
    #STATE MACHINE FUNCTION
    def update_state(self):

        last_state_temp = None

        #Get Last state first. Pull appropriate varibale coresponding to that timeframe.
        #Essentially case statement but case is only supported python 3.10
        if(self.current_timeframe_string == "Week"):
            last_state_temp = self.trend_child_Week
        if(self.current_timeframe_string == "Day"):
                last_state_temp = self.trend_child_Day
        if(self.current_timeframe_string == "Hour"):
            last_state_temp = self.trend_child_Hour
        if(self.current_timeframe_string == "30min"):
            last_state_temp = self.trend_child_30min
        if(self.current_timeframe_string == "15min"):
            last_state_temp = self.trend_child_15min
        if(self.current_timeframe_string == "5min"):
            last_state_temp = self.trend_child_5min
        if(self.current_timeframe_string == "1min"):
            last_state_temp = self.trend_child_1min

        state_machine(last_state_temp)

####################################################################################################
####################################################################################################
    def state_machine(self, last_state):        

        #temp variable
        new_state = None

        #Based on the last State update the current State for that trend        
        
        #State 1: confirmed_uptrend
        if(last_state == trend_state.confirmed_uptrend):

            #Possibilities include: go back to state 1 or go to state 2 (6 combinations)
            #State :1 -> 2 (combination 1)
            if((self.higher_high_counter == 0) and ( self.higher_low_counter >= 2) and (self.lower_low_counter == 0) and (self.lower_high_counter == 1)):
                new_state = trend_state.possible_uptrend_reversal

            #State :1 -> 2 (combination 2)
            elif((self.higher_high_counter == 0) and ( self.higher_low_counter == 0) and (self.lower_low_counter == 1) and (self.lower_high_counter == 1)):
                new_state = trend_state.possible_uptrend_reversal

            #State :1 -> 2 (combination 3)
            elif((self.higher_high_counter == 0) and ( self.higher_low_counter == 0) and (self.lower_low_counter == 1) and (self.lower_high_counter == 2)):
                new_state = trend_state.possible_uptrend_reversal

            #State :1 -> 2 (combination 4)
            elif((self.higher_high_counter >= 2) and ( self.higher_low_counter == 0) and (self.lower_low_counter == 1) and (self.lower_high_counter == 0)):
                new_state = trend_state.possible_uptrend_reversal

            #State :1 -> 2 (combination 5)
            elif((self.higher_high_counter == 0) and ( self.higher_low_counter == 0) and (self.lower_low_counter == 1) and (self.lower_high_counter == 1)):
                new_state = trend_state.possible_uptrend_reversal

            #State :1 -> 2 (combination 6)
            elif((self.higher_high_counter == 0) and (self.higher_low_counter == 0) and (self.lower_low_counter == 2) and (self.lower_high_counter == 1)):
                new_state = trend_state.possible_uptrend_reversal

            #Stay at confirmed Uptrend State: 1 - > 1
            else:
                new_state = last_state


        #State 2: possible_uptrend_reversal to downside
        if(last_state == trend_state.possible_uptrend_reversal):

            #Four possible Scenarios: Stay at state 2, go to state 6, go to state 5 or go to state 3
            #State: 2 -> 6
            if((self.higher_high_counter >= 2) and ( self.higher_low_counter == 0) and (self.lower_low_counter >= 2) and (self.lower_high_counter == 0)):
                new_state = trend_state.volitility_expansion

            #State: 2 -> 5
            elif((self.higher_high_counter == 0) and ( self.higher_low_counter >= 2) and (self.lower_low_counter == 0) and (self.lower_high_counter >= 2)):
                new_state = trend_state.volitility_contraction

            #State: 2 -> 3
            elif((self.higher_high_counter == 0) and ( self.higher_low_counter == 0) and (self.lower_low_counter >= 2) and (self.lower_high_counter >= 2)):
                new_state = trend_state.confirmed_downtrend

            #Stay at State. State: 2 -> 2
            else((self.higher_high_counter == 0) and ( self.higher_low_counter == 0) and (self.lower_low_counter >= 2) and (self.lower_high_counter >= 2)):
                new_state = trend_state.possible_downtrend_reversal



        #State 3: confirmed_downtrend
        if(last_state == trend_state.confirmed_downtrend):

            #Possibilities include: go back to state 3 or go to state 4 (6 combinations)
            #State:3 -> 4 (combination 1)
            if((self.higher_high_counter == 1) and ( self.higher_low_counter == 0) and (self.lower_low_counter >= 2) and (self.lower_high_counter == 0)):
                new_state = trend_state.possible_downtrend_reversal

            #State:3 -> 4 (combination 2)
            if((self.higher_high_counter == 1) and ( self.higher_low_counter == 1) and (self.lower_low_counter == 0) and (self.lower_high_counter == 0)):
                new_state = trend_state.possible_downtrend_reversal

            #State:3 -> 4 (combination 3)
            if((self.higher_high_counter == 2) and ( self.higher_low_counter == 1) and (self.lower_low_counter == 0) and (self.lower_high_counter == 0)):
                new_state = trend_state.possible_downtrend_reversal

            #State:3 -> 4 (combination 4)
            if((self.higher_high_counter == 0) and ( self.higher_low_counter == 1) and (self.lower_low_counter == 0) and (self.lower_high_counter >= 2)):
                new_state = trend_state.possible_downtrend_reversal

            #State:3 -> 4 (combination 5)
            if((self.higher_high_counter == 1) and ( self.higher_low_counter == 1) and (self.lower_low_counter == 0) and (self.lower_high_counter == 0)):
                new_state = trend_state.possible_downtrend_reversal

            #State:3 -> 4 (combination 6)
            if((self.higher_high_counter == 1) and (self.higher_low_counter == 2) and (self.lower_low_counter == 0) and (self.lower_high_counter == 0)):
                new_state = trend_state.possible_downtrend_reversal

            #Stay at confirmed downtrend State 3 -> 3
            else:
                new_state = last_state


        #State 4: possible_downtrend_reversal
        if(last_state == trend_state.possible_downtrend_reversal):


        #State 5: volitility_contraction
        if(last_state == trend_state.volitility_contraction):


        #State 6: volitility_expansion
        if(last_state == trend_state.volitility_expansion):


        #State 7: starting_state
        if(last_state == trend_state.starting_state):
            
            #Can only go to state 1 or 3 or stay same
            #State :7 -> 1
            if((self.higher_high_counter >= 2) and ( self.higher_low_counter >= 2) and (self.lower_low_counter == 0) and (self.lower_high_counter == 0)):
                new_state = trend_state.confirmed_uptrend

            #State :7 -> 3
            elif((self.higher_high_counter == 0) and ( self.higher_low_counter == 0) and (self.lower_low_counter >= 2) and (self.lower_high_counter >= 2)):
                new_state = trend_state.confirmed_downtrend
            
            #Stay at State
            else:
                new_state = last_state

        #State 8: debug# Used for troubleshooting
        if((last_state == trend_state.debug) or (new_state == None)):
            logging.error("Error: Reached State 8 (New State likelly not set correctly in state machine)")


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
    market_health.get_price_estimate(api, index_group)
    market_health.get_starting_trend(api, index_group)

    #print("TEST FROM MAIN FUNCTION", index_group.stock_objects_array[3].name, index_group.stock_objects_array[3].EMA_21)

    #Test Print Object Funciton
    index_group.print_group_data()
    



    #Populate index_group


main()