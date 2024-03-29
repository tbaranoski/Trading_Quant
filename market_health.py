#### The Purpose of this file is to look at Market Internals and Metrics which determine the health of the trend.
#### The file will return different scores which will then be used when managing the portfolio. 

#### Low Scores: Suggest trimming profitable positions into strength(2-3 ATR from 21 EMA), cutting low Relative strength stocks
#### and becoming more picky with future entries for the short term. (A bigger emphasis on TML (True Market Leaders) and heavy volume breakouts)

#### High scores: Suggest Positions can be swung for longer, portfolio exposure can increase if some of psoitions are in profit and stop-loss gets move up.
####: Less picky on future entries with the focus on stocks form the leading sectors.

##Distribution Day: A day where market index drops by more than .2% with greater volume than the day before. Indicates Institutional selling AKA Distribution.
##########################################################################################################################################################
#import alpaca_trade_api as tradeapi
from asyncio.windows_events import NULL
from calendar import week
from unicodedata import name
from alpaca_trade_api.rest import REST, TimeFrame
import datetime as dt #to get date
import pytz #to get date
import math #rounding purposes
import web_socket_daily_bar #Needs to be dubugged later
import pandas as pd 

#api_test = REST()
#import alpaca_trad_api #delete
import time
from pytz import timezone
import logging #added for logging purposes
import logging.handlers #added for logging purposes

#Constants
PERCENT_TO_BE_DISTRIBUTION = -.2
LONG_DISTRIBUTION_NUMBER = 25
SHORT_DISTRIBUTION_NUMBER = 7

#CONSTANT COMPUTATIONS
#Extra Days added to account for weekend and Holidays
LONG_DISTRIBUTION = math.ceil((LONG_DISTRIBUTION_NUMBER *((8/5)) + 10))
SHORT_DISTRIBUTION =  math.ceil((SHORT_DISTRIBUTION_NUMBER *((8/5)) + 10))

#############################################################################################################################################
#Print Distribution Days for Major Indexes
def print_distribution_day(distribution_array):
    print("Distribution Day Count($SPY) over last",LONG_DISTRIBUTION_NUMBER, " days: ", distribution_array[0])
    print("Distribution Day Count($SPY) over last",SHORT_DISTRIBUTION_NUMBER, " days: ", distribution_array[1])
    print("Distribution Day Count($QQQ) over last",LONG_DISTRIBUTION_NUMBER, " days: ", distribution_array[2])
    print("Distribution Day Count($QQQ) over last",SHORT_DISTRIBUTION_NUMBER, " days: ", distribution_array[3])
    print("Distribution Day Count($DIA) over last",LONG_DISTRIBUTION_NUMBER, " days: ", distribution_array[4])
    print("Distribution Day Count($DIA) over last",SHORT_DISTRIBUTION_NUMBER, " days: ", distribution_array[5])
    print("Distribution Day Count($IWO) over last",LONG_DISTRIBUTION_NUMBER, " days: ", distribution_array[6])
    print("Distribution Day Count($IWO) over last",SHORT_DISTRIBUTION_NUMBER, " days: ", distribution_array[7])
    print("Distribution Day Count($IWM) over last",LONG_DISTRIBUTION_NUMBER, " days: ", distribution_array[8])
    print("Distribution Day Count($IWM) over last",SHORT_DISTRIBUTION_NUMBER, " days: ", distribution_array[9])

#FOR TESTING BAR VALUES
def print_Close(NUM_DAYS, TICKER_D_BARS):
    lenght_data = len(TICKER_D_BARS)
    for i in range (lenght_data):
        print("Index: ", i, "Date: ", TICKER_D_BARS[i].t, "Close: ", TICKER_D_BARS[i].c )
############################################################################################################################################
############################################################################################################################################


##Returns Distribution Day Count
def get_Distribution_DAY_COUNT(NUM_DAYS, TICKER_D_BARS):
    distribution_days = 0

    #Get Start Index
    start_index = (len(TICKER_D_BARS)) - NUM_DAYS
    end_index = (len(TICKER_D_BARS)) - 1

    #Itterate through start and end index
    for i in range (start_index, end_index):
        #Calculate percentage chnage from yesterdays close
        change_percent = ((((TICKER_D_BARS[i+1].c) - (TICKER_D_BARS[i].c)) / (TICKER_D_BARS[i].c))) * 100

        # IF index dropped by more than .2% look at volume comparison between yesterday and today
        if(change_percent <= PERCENT_TO_BE_DISTRIBUTION):
            if((TICKER_D_BARS[i+1].v - (TICKER_D_BARS[i].v)) > 0):                
                distribution_days = distribution_days + 1
                

    return distribution_days
#############################################################################################################################################
#Main function in file
def get_distribution_health(api, group):
    
    ###################################################################################
    ###################################################################################
    #calculate Distribution Day Count For Major Indexes ($SPY, $QQQ, $DIA, $IWO, $IWM)
    # over a longer period (currentlly lsast 25 days) and over a shorter period (last 7 days)
    ###################################################################################
    ###################################################################################

    #Calculate start_time since get_bars works in reverse for get_bars (V2 endpoint)
    #Reference https://forum.alpaca.markets/t/get-bars-vs-get-barset/8127/6
    timeNow = dt.datetime.now(pytz.timezone('US/Eastern'))
    start_time_long_distribution = timeNow - dt.timedelta(days=LONG_DISTRIBUTION)
    
    #for every stock in the group, calculate Distribution Day Count. Used primarilly For Major Indexes ($SPY, $QQQ, $DIA, $IWO, $IWM)
    # over a longer period (currentlly lsast 25 days) and over a shorter period (last 7 days)
    for stock in group.stock_objects_array:

        #logging message to print names being processed
        temp_string = "DATA BEING COLLECTED FOR " + stock.name + " object ******"
        logging.info(temp_string)
        
        #Get DAILY BARS for stock
        temp_D_BARSET = api.get_bars(stock.name, TimeFrame.Day, start = start_time_long_distribution.isoformat(), end = None, limit = LONG_DISTRIBUTION)

        # Calculate Short and Long Distribution Day Count
        # Populate Stock object with the Long Distribution and Short Distribution Count
        stock.distribution_Long_len = get_Distribution_DAY_COUNT(LONG_DISTRIBUTION_NUMBER, temp_D_BARSET)
        stock.distribution_Short_len = get_Distribution_DAY_COUNT(SHORT_DISTRIBUTION_NUMBER, temp_D_BARSET)
    
        #Clear Temp Arrays
        temp_D_BARSET = []        

##############################################################################################################################    
##############################################################################################################################
#GET 9ema AND 21 ema on DAILY CHART
def get_ema_health(api, group):

    #Constants
    SHORT_EMA = 9
    LONG_EMA = 21

    #Computations to get extra bars since get_bars() will count weekends and holidays as a day
    #math.ceil((LONG_DISTRIBUTION_NUMBER *((7/5)) + 10))
    DATA_PERIOD = math.ceil((((LONG_EMA * 2) * (7/5)) + 10))
    timeNow = dt.datetime.now(pytz.timezone('US/Eastern'))
    start_time_long_emas = timeNow - dt.timedelta(days=DATA_PERIOD)
    start_time_hours = (timeNow - dt.timedelta(hours=60)).isoformat()

    
    #Itterate through the list of stocks in group and get EMA health
    for stock in group.stock_objects_array:

        #Get Daily bar data then parse only the Closes
        temp_D_BARSET = api.get_bars(stock.name, TimeFrame.Day, start = start_time_long_emas.isoformat(), end = None, limit = DATA_PERIOD)
        temp_EMA_C = parse_closes(temp_D_BARSET)

        #Get an Estimate of the Current Price Right Now (AKA Todays current close) and parse only candle closes
        last_few_hours_temp = api.get_bars(stock.name, TimeFrame.Hour, start = start_time_hours, end = None, limit = 60)
        last_few_hours_temp_C = parse_closes(last_few_hours_temp)

        #Get Most Current Hourly Close and append to dataset
        len_temp = len(last_few_hours_temp_C)
        temp_price_now = last_few_hours_temp_C[len_temp - 1]
        temp_EMA_C.append(temp_price_now)

        #Compute Long and Short EMA arrays for each index and populate stock object with current EMA data

        temp_EMA_21_array = ema(temp_EMA_C, LONG_EMA)
        temp_EMA_9_array = ema(temp_EMA_C, SHORT_EMA)

        stock.EMA_21 = temp_EMA_21_array[len(temp_EMA_21_array) - 1]
        stock.EMA_9 = temp_EMA_9_array[len(temp_EMA_9_array) - 1]

        #Clear temp Arrays and Varibales
        del temp_D_BARSET,temp_EMA_C, last_few_hours_temp, last_few_hours_temp_C, len_temp, temp_price_now, temp_EMA_21_array, temp_EMA_9_array


########################################################################################################################
########################################################################################################################
### Parse CLosing Data ##########
def parse_closes(RAW_DATA):
    temp_array = []
    
    for i in range((len(RAW_DATA)) -1):
        temp_array.append(RAW_DATA[i].c)

    return temp_array
################################################################################################################
########################################################################################################################


################################################################################################################
#Function TAKEN FROM https://stackoverflow.com/questions/488670/calculate-exponential-moving-average-in-python
def ema(s, n):
    """
    returns an n period exponential moving average for
    the time series s

    s is a list ordered from oldest (index 0) to most
    recent (index -1)
    n is an integer

    returns a numeric array of the exponential
    moving average
    """
    #s = array(s)
    ema = []
    j = 1

    #get n sma first and calculate the next n period ema
    sma = sum(s[:n]) / n
    multiplier = 2 / float(1 + n)
    ema.append(sma)

    #EMA(current) = ( (Price(current) - EMA(prev) ) x Multiplier) + EMA(prev)
    ema.append(( (s[n] - sma) * multiplier) + sma)

    #now calculate the rest of the values
    for i in s[n+1:]:
        tmp = ( (i - ema[j]) * multiplier) + ema[j]
        j = j + 1
        ema.append(tmp)

    return ema
    ################################################################################################################
    ################################################################################################################

def get_price_estimate(api, group):

    # Check if the market is open now. Code From Reference
    #Reference: https://alpaca.markets/deprecated/docs/api-documentation/how-to/market-hours/#:~:text=See%20if%20the%20Market%20is,closed%20on%20a%20particular%20date.
    clock = api.get_clock()
    timeNow = dt.datetime.now(pytz.timezone('US/Eastern'))

    #Determine if market is OPEN OR CLOSES
    #IF market OPEN, pull most recent minute candles
    if(clock.is_open):
        logging.info("Algorithm Determined Market is OPEN  from:get_price_estimate()")

        #Itterate through the list of stocks in group and get most recent MINUTE close. Store attribute as current_price_estimate 
        for stock in group.stock_objects_array:
            start_time_hours = (timeNow - dt.timedelta(hours=1)).isoformat()

            last_few_hours_temp = api.get_bars(stock.name, TimeFrame.Minute, start = start_time_hours, end = None, limit = 120)
            last_few_hours_temp_C = parse_closes(last_few_hours_temp)
            len_temp = len(last_few_hours_temp_C)        
            stock.current_price_estimate = last_few_hours_temp_C[len_temp - 1]

            del start_time_hours, last_few_hours_temp, last_few_hours_temp_C, len_temp
            
    #IF market CLOSED, pull most recent hour candles. Make sure if it is Sunday we can still pull Friday's data
    else:
        logging.info("Algorithm Determined Market is CLOSED  from:get_price_estimate()")
        
        #Itterate through the list of stocks in group and get most recent HOUR close. Store attribute as current_price_estimate 
        for stock in group.stock_objects_array:
            start_time_hours = (timeNow - dt.timedelta(hours=60)).isoformat()

            last_few_hours_temp = api.get_bars(stock.name, TimeFrame.Hour, start = start_time_hours, end = None, limit = 60)
            last_few_hours_temp_C = parse_closes(last_few_hours_temp)
            len_temp = len(last_few_hours_temp_C)        
            stock.current_price_estimate = last_few_hours_temp_C[len_temp - 1]

            del start_time_hours, last_few_hours_temp, last_few_hours_temp_C, len_temp

################################################################################################################
################################################################################################################
###   Get Daily Bars Helper function for a specific stock
def get_Dataset_D(api, stock, DATA_PERIOD = 260):

    timeNow = dt.datetime.now(pytz.timezone('US/Eastern'))
    start_time = timeNow - dt.timedelta(days=DATA_PERIOD)
    start_time_hours = (timeNow - dt.timedelta(hours=60)).isoformat()

    #Determine Daily trend by pulling daily bars
    temp_D_BARSET = api.get_bars(stock.name, TimeFrame.Day, start = start_time.isoformat(), end = None, limit = DATA_PERIOD)
    temp_D_BARSET_PARSED = parse_closes(temp_D_BARSET)

    last_few_hours_temp = api.get_bars(stock.name, TimeFrame.Hour, start = start_time_hours, end = None, limit = 60)
    last_few_hours_temp_C = parse_closes(last_few_hours_temp)

    #Get Most Current Hourly Close and append to dataset
    len_temp = len(last_few_hours_temp_C)
    temp_price_now = last_few_hours_temp_C[len_temp - 1]
    temp_D_BARSET_PARSED.append(temp_price_now)

    #Store attribute and return dataset
    stock.dataset = temp_D_BARSET_PARSED
    return temp_D_BARSET_PARSED

################################################################################################################
def get_Dataset_W(api, stock, DATA_PERIOD = 100):
    timeNow = dt.datetime.now(pytz.timezone('US/Eastern'))
    start_time = timeNow - dt.timedelta(weeks=DATA_PERIOD)
    start_time_hours = (timeNow - dt.timedelta(hours=60)).isoformat()

    #Determine Weekly trend by pulling daily bars
    temp_W_BARSET = api.get_bars(stock.name, TimeFrame.Week, start = start_time.isoformat(), end = None, limit = DATA_PERIOD)
    temp_W_BARSET_PARSED = parse_closes(temp_W_BARSET)

    last_few_hours_temp = api.get_bars(stock.name, TimeFrame.Hour, start = start_time_hours, end = None, limit = 60)
    last_few_hours_temp_C = parse_closes(last_few_hours_temp)

    #Get Most Current Hourly Close and append to dataset
    len_temp = len(last_few_hours_temp_C)
    temp_price_now = last_few_hours_temp_C[len_temp - 1]
    temp_W_BARSET_PARSED.append(temp_price_now)

    #Store attribute and return dataset
    stock.dataset = temp_W_BARSET_PARSED
    return temp_W_BARSET_PARSED


################################################################################################################
def get_Dataset_3D(api, stock, DATA_PERIOD = 780):
    timeNow = dt.datetime.now(pytz.timezone('US/Eastern'))
    start_time = timeNow - dt.timedelta(days=DATA_PERIOD)
    start_time_hours = (timeNow - dt.timedelta(hours=60)).isoformat()

    #Determine 3 Day trend by pulling daily bars and take every three
    temp_3D_BARSET = api.get_bars(stock.name, TimeFrame.Day, start = start_time.isoformat(), end = None, limit = DATA_PERIOD)
    temp_3D_BARSET_PARSED = parse_closes(temp_3D_BARSET)

    last_few_hours_temp = api.get_bars(stock.name, TimeFrame.Hour, start = start_time_hours, end = None, limit = 60)
    last_few_hours_temp_C = parse_closes(last_few_hours_temp)

    #Get Most Current Hourly Close and append to dataset
    len_temp = len(last_few_hours_temp_C)
    temp_price_now = last_few_hours_temp_C[len_temp - 1]
    temp_3D_BARSET_PARSED.append(temp_price_now)

    #Store attribute and return dataset
    new_data = skip_parse(interval = 3, data = temp_3D_BARSET_PARSED)
    #stock.dataset = temp_3D_BARSET_PARSED
    return new_data


################################################################################################################
######    Gets the baset for the Hourly or Minute Timeframe   ####
def get_Dataset_IntraDay(api, stock, DATA_PERIOD = 260, temp_timeframe = "Hour"):

    timeNow = dt.datetime.now(pytz.timezone('US/Eastern'))
    start_time_hours = None
    timeframe = None

    #Determine what start time should be based on timeframe. Pull extra bars for one minute timeframe in case we are computing after hours

    if(temp_timeframe == "Hour"):
        start_time_hours = (timeNow - dt.timedelta(hours=DATA_PERIOD)).isoformat()
        timeframe = TimeFrame.Hour

    elif(temp_timeframe == "30min"):
        start_time_hours = (timeNow - dt.timedelta(hours=DATA_PERIOD)).isoformat()
        timeframe = TimeFrame.Minute
    
    elif(temp_timeframe == "15min"):
        start_time_hours = (timeNow - dt.timedelta(hours= (DATA_PERIOD / 2))).isoformat()
        timeframe = TimeFrame.Minute

    elif(temp_timeframe == "5min"):
        start_time_hours = (timeNow - dt.timedelta(hours= (DATA_PERIOD / 4))).isoformat()
        timeframe = TimeFrame.Minute

    elif(temp_timeframe == "1min"):
        DATA_PERIOD = DATA_PERIOD
        start_time_hours = (timeNow - dt.timedelta(hours=(DATA_PERIOD / 60))).isoformat()
        timeframe = TimeFrame.Minute
    else:
        temp_error = "timeframe in get_Dataset_IntraDay() is: " + temp_timeframe
        logging.error(temp_error)
        logging.error("Timeframe in get_Dataset_IntraDay() Not Recognized")


    #Determine IntraDay Trend bars for that timeframe
    temp_intra_BARSET = api.get_bars(stock.name, timeframe, start = start_time_hours, end = None) #limit = DATA_PERIOD)

    temp_intra_BARSET_MARKET = [] #declare variable

    #Get rid of pre/post market data. Keep only market data during market hours between 09:30 and 16:00. 
    #Combine minute candles for 30min, 15 min, and 5 min
    if(temp_timeframe == "Hour" or temp_timeframe == "30min" or temp_timeframe == "15min" or temp_timeframe == "5min"):
        temp_intra_BARSET_MARKET = only_market_hours(temp_intra_BARSET, timeframe = temp_timeframe)
    
    elif(temp_timeframe == "1min"):
        #parse closes
        temp_intra_BARSET_MARKET = parse_closes(temp_intra_BARSET)
    
    else:
        logging.error("ERROR with timeframe in get_Dataset_IntraDay")

    #Store attribute and return dataset
    stock.dataset = temp_intra_BARSET_MARKET
    return temp_intra_BARSET_MARKET

###################################################################################################################
###################################################################################################################
#Removes pre/post market data leaving only market data.
#In addition if the timeframe is 5min, 15 min, or 30min combine the 1 min candles to form larger timeframe candle
def only_market_hours(RAW_DATA, timeframe):

    parsed_array = []
    #Get rid of pre market and post-market data points and return an array of closing prices
    df_data = (RAW_DATA.df)
    new_df_data = df_data.between_time('09:30' , '16:00')

    #Convert datatframe to array
    #If timeframe is Hour go from dataframe -> Array
    if(timeframe == "Hour"):
        parsed_array = new_df_data.loc[:]['close'].values

    #If timeframe is 30min use for loop to pull 30 min closes
    elif(timeframe == "30min"):

        parsed_array = new_df_data.iloc[::30, :]['close'].values
        
         
        #Get rid of 0th index, and append current price to end
        #parsed_array.pop(0)
        #parsed_array.append(RAW_DATA[len(RAW_DATA) - 1].c)    
        #print(parsed_array)
        #print("type is:", type(parsed_array))

    #If timeframe is 15min use for loop to pull 30 min closes
    #elif(timeframe == "15min"):
        #for i in range(15 - 1, len(new_df_data.columns) - 1, 15):
            #parsed_array = new_df_data.loc[i]['close'].values

    #If timeframe is 15min use for loop to pull 30 min closes
    #elif(timeframe == "5min"):
        #for i in range(5 - 1, len(new_df_data.columns) - 1, 5):
            #parsed_array = new_df_data.loc[i]['close'].values

    #else:
        #error_string = "Timeframe not recognized in only_market_hours() in markethealth.py. Timeframe is: " + timeframe
        #logging.error(error_string)

    return parsed_array


################################################################################################################
################################################################################################################
#Parses data by skipping by interval and removing data not needed to get custom timeframes
def skip_parse(interval = 3, data = None):
    
    parsed_data = []

    #Take a data point every interval length
    for i in range(0, len(data) - 1, interval):
        parsed_data.append(data[i])

    #Take final (partial/current data point if it has not been taken yet)
    parsed_data.append(data[len(data) - 1])

    return parsed_data

#### Initialzes the timeframe, dataset for that timeframe(candle closes) and clears markers
def initialize_trend_data(stock_obj, timeframe_string, dataset):
    
    #Manually set timefram and initialize via function
    stock_obj.current_timeframe_string = timeframe_string
    stock_obj.set_timeframe_initial()

    #Set dataset
    del stock_obj.dataset
    stock_obj.dataset = dataset

################################################################################################################
################################################################################################################

### Use historical data to determine the current trend on specified timeframe(s)   ####
def get_starting_trends(api, group):

    #Function Constants (Amount of bars taken for computations)
    DATA_PERIOD_DAY = 260 

    #For each stock start by getting Daily Data Set
    for stock_obj in group.stock_objects_array:

        dataset_daily = get_Dataset_D(api, stock_obj, DATA_PERIOD_DAY)
        initialize_trend_data(stock_obj, "Day", dataset_daily)
        stock_obj.determine_ititial_trend()

    #####################################################################
    #For each stock Get Hourly Timeframe
    for stock_obj in group.stock_objects_array:

        dataset_hourly = get_Dataset_IntraDay(api, stock_obj, DATA_PERIOD_DAY * 3, "Hour")
        initialize_trend_data(stock_obj, "Hour", dataset_hourly)
        stock_obj.determine_ititial_trend()

    #####################################################################
    #For each stock Get Minute Timeframe
    for stock_obj in group.stock_objects_array:

        dataset_min = get_Dataset_IntraDay(api, stock_obj, DATA_PERIOD_DAY * 3, "1min")
        initialize_trend_data(stock_obj, "1min", dataset_min)
        stock_obj.determine_ititial_trend()

    ###############################################################################
    #####    CONSTRUCTOIN START    ################################################
    #For each stock start by getting Weekly Data Set
    for stock_obj in group.stock_objects_array:

        dataset_weekly = get_Dataset_W(api, stock_obj, 100)
        initialize_trend_data(stock_obj, "Week", dataset_weekly)
        stock_obj.determine_ititial_trend()

    #3D Datatset
    for stock_obj in group.stock_objects_array:
    
        dataset_3D = get_Dataset_3D(api, stock_obj, DATA_PERIOD_DAY * 3)
        initialize_trend_data(stock_obj, "3D", dataset_3D)
        stock_obj.determine_ititial_trend()

    #30 Min Datatset
    for stock_obj in group.stock_objects_array:

        dataset_30min = get_Dataset_IntraDay(api, stock_obj, 1000, "30min")

        print("!!!!@@@@: size of arrray is", len(dataset_30min))

        initialize_trend_data(stock_obj, "30min", dataset_30min)
        stock_obj.determine_ititial_trend()

    #15 Min Datatset
    #for stock_obj in group.stock_objects_array:

        #dataset_15min = get_Dataset_IntraDay(api, stock_obj, 1400, "15min")
        #initialize_trend_data(stock_obj, "15min", dataset_15min)
        #stock_obj.determine_ititial_trend()

    #5 Min Datatset
    #for stock_obj in group.stock_objects_array:

        #dataset_5min = get_Dataset_IntraDay(api, stock_obj, 1400, "5min")
        #initialize_trend_data(stock_obj, "5min", dataset_5min)
        #stock_obj.determine_ititial_trend()

     ###############################################################################
    #####    END    ################################################

#calculate SMAS
def get_sma_health(api, group_name):
    DATA_PERIOD_DAY = int((200 *(8/5)) + 10)

    #Get Daily data
    for name in group_name.stock_objects_array:
        dataset_daily = get_Dataset_D(api, name, DATA_PERIOD_DAY)

        #Get 200 SMA on Daily
        sma_200 = sma(dataset_daily, 200, name.name)

        #Get 50 SMA on Daily
        sma_50 = sma(dataset_daily, 50, name.name)

        #Store SMA attributes in stock object
        name.SMA_200 = sma_200
        name.SMA_50 = sma_50
    

def sma(data, length_sma , stock_name):

    current_sma = None
    length_data_set = len(data)
    start_index = length_data_set - length_sma
    
    #Compute SMA
    total = 0    
    try:
        for i in range(start_index, length_data_set):
            total = total + data[i]
        current_sma = round(total / length_sma, 2)       

    except:
        temp_error = "SMA can not be computed for: " + stock_name
        logging.error(temp_error)

    return current_sma