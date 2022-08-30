#### The Purpose of this file is to look at Market Internals and Metrics which determine the health of the trend.
#### The file will return different scores which will then be used when managing the portfolio. 

#### Low Scores: Suggest trimming profitable positions into strength(2-3 ATR from 21 EMA), cutting low Relative strength stocks
#### and becoming more picky with future entries for the short term. (A bigger emphasis on TML (True Market Leaders) and heavy volume breakouts)

#### High scores: Suggest Positions can be swung for longer, portfolio exposure can increase if some of psoitions are in profit and stop-loss gets move up.
####: Less picky on future entries with the focus on stocks form the leading sectors.

##Distribution Day: A day where market index drops by more than .2% with greater volume than the day before. Indicates Institutional selling AKA Distribution.
##########################################################################################################################################################
#import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import REST, TimeFrame
import datetime as dt #to get date
import pytz #to get date
import math #rounding purposes
#api_test = REST()
#import alpaca_trad_api #delete

#Constants
PERCENT_TO_BE_DISTRIBUTION = -.2
LONG_DISTRIBUTION_NUMBER = 25
SHORT_DISTRIBUTION_NUMBER = 7

#CONSTANT COMPUTATIONS
#To account for Sunday and Saturday which are not actual trading days. + 10 accounts for any holidays
LONG_DISTRIBUTION = math.ceil((LONG_DISTRIBUTION_NUMBER *((7/5)) + 10))
SHORT_DISTRIBUTION =  math.ceil((SHORT_DISTRIBUTION_NUMBER *((9/7)) + 10))

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
def get_distribution_health(api):
    
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

    #Get DAILY BARS for SPY and QQQ and DIA, IWO, and IWM
    SPY_D_BARSET = api.get_bars('SPY', TimeFrame.Day, start = start_time_long_distribution.isoformat(), end = None, limit = LONG_DISTRIBUTION)
    QQQ_D_BARSET = api.get_bars('QQQ', TimeFrame.Day, start = start_time_long_distribution.isoformat(), end = None, limit = LONG_DISTRIBUTION)
    DIA_D_BARSET = api.get_bars('DIA', TimeFrame.Day, start = start_time_long_distribution.isoformat(), end = None, limit = LONG_DISTRIBUTION)
    IWO_D_BARSET = api.get_bars('IWO', TimeFrame.Day, start = start_time_long_distribution.isoformat(), end = None, limit = LONG_DISTRIBUTION)
    IWM_D_BARSET = api.get_bars('IWM', TimeFrame.Day, start = start_time_long_distribution.isoformat(), end = None, limit = LONG_DISTRIBUTION)

    #Calculate distribution days
    SPY_DIST_LONG = get_Distribution_DAY_COUNT(LONG_DISTRIBUTION_NUMBER, SPY_D_BARSET)
    SPY_DIST_SHORT = get_Distribution_DAY_COUNT(SHORT_DISTRIBUTION_NUMBER, SPY_D_BARSET)
    QQQ_DIST_LONG = get_Distribution_DAY_COUNT(LONG_DISTRIBUTION_NUMBER, QQQ_D_BARSET)
    QQQ_DIST_SHORT = get_Distribution_DAY_COUNT(SHORT_DISTRIBUTION_NUMBER, QQQ_D_BARSET)
    DIA_DIST_LONG = get_Distribution_DAY_COUNT(LONG_DISTRIBUTION_NUMBER, DIA_D_BARSET)
    DIA_DIST_SHORT = get_Distribution_DAY_COUNT(SHORT_DISTRIBUTION_NUMBER, DIA_D_BARSET)
    IWO_DIST_LONG = get_Distribution_DAY_COUNT(LONG_DISTRIBUTION_NUMBER, IWO_D_BARSET)
    IWO_DIST_SHORT = get_Distribution_DAY_COUNT(SHORT_DISTRIBUTION_NUMBER, IWO_D_BARSET)
    IWM_DIST_LONG = get_Distribution_DAY_COUNT(LONG_DISTRIBUTION_NUMBER, IWM_D_BARSET)
    IWM_DIST_SHORT = get_Distribution_DAY_COUNT(SHORT_DISTRIBUTION_NUMBER, IWM_D_BARSET)

    distribution_array_indexes = [SPY_DIST_LONG,SPY_DIST_SHORT,QQQ_DIST_LONG,QQQ_DIST_SHORT,DIA_DIST_LONG,DIA_DIST_SHORT,IWO_DIST_LONG,IWO_DIST_SHORT,IWM_DIST_LONG,IWM_DIST_SHORT]
    print_distribution_day(distribution_array_indexes)

    return distribution_array_indexes

#Determine if Indexes are above 9ema AND 21 ema on DAILY CHART
def get_ema_health(api):

    #Constants
    SHORT_EMA = 9
    LONG_EMA = 21

    #Computations to get extra bars since get_bars() will count weekends and holidays as a day
    #math.ceil((LONG_DISTRIBUTION_NUMBER *((7/5)) + 10))
    DATA_PERIOD = math.ceil((((LONG_EMA * 2) * (7/5)) + 10))
    timeNow = dt.datetime.now(pytz.timezone('US/Eastern'))
    start_time_long_emas = timeNow - dt.timedelta(days=DATA_PERIOD)

    #Get Daily bar data
    SPY_EMA = api.get_bars('SPY', TimeFrame.Day, start = start_time_long_emas.isoformat(), end = None, limit = DATA_PERIOD)
    QQQ_EMA = api.get_bars('QQQ', TimeFrame.Day, start = start_time_long_emas.isoformat(), end = None, limit = DATA_PERIOD)
    DIA_EMA = api.get_bars('DIA', TimeFrame.Day, start = start_time_long_emas.isoformat(), end = None, limit = DATA_PERIOD)
    IWM_EMA = api.get_bars('IWM', TimeFrame.Day, start = start_time_long_emas.isoformat(), end = None, limit = DATA_PERIOD)
    IWO_EMA = api.get_bars('IWO', TimeFrame.Day, start = start_time_long_emas.isoformat(), end = None, limit = DATA_PERIOD)
    
    #Test print to make sure data is not messed up
    #print_Close(DATA_PERIOD, SPY_EMA)

    #Compute Exponential average using ema funciton. Pass in closing values
    #Start by parsing only the candle closes
    SPY_EMA_C = parse_closes(SPY_EMA)
    QQQ_EMA_C = parse_closes(QQQ_EMA)
    DIA_EMA_C = parse_closes(DIA_EMA)
    IWM_EMA_C = parse_closes(IWM_EMA)
    IWO_EMA_C = parse_closes(IWO_EMA)

    #Compute Long and Short EMA for each index

    SPY_21D_EMA = ema(SPY_EMA_C, LONG_EMA)
    SPY_9D_EMA = ema(SPY_EMA_C, SHORT_EMA)

    QQQ_21D_EMA = ema(QQQ_EMA_C, LONG_EMA)
    QQQ_9D_EMA = ema(QQQ_EMA_C, SHORT_EMA)

    DIA_21D_EMA = ema(DIA_EMA_C, LONG_EMA)
    DIA_9D_EMA = ema(DIA_EMA_C, SHORT_EMA)

    IWM_21D_EMA = ema(IWM_EMA_C, LONG_EMA)
    IWM_9D_EMA = ema(IWM_EMA_C, SHORT_EMA)

    IWO_21D_EMA = ema(IWO_EMA_C, LONG_EMA)
    IWO_9D_EMA = ema(IWO_EMA_C, SHORT_EMA)


    #test print for allignment purposes

    #todays close
    end = len(SPY_EMA_C)
    print("RIGHT NOW ON SPY IS: ", SPY_EMA_C[end-1])

    print (SPY_21D_EMA)
    print("The length of the array is: ", len(SPY_21D_EMA))


    print("\n\n\n")
    print (SPY_9D_EMA)
    print("The length of the array is: ", len(SPY_9D_EMA))

################################################################################################################
### Parse CLosing Data ##########
def parse_closes(RAW_DATA):
    temp_array = []
    
    for i in range((len(RAW_DATA)) -1):
        temp_array.append(RAW_DATA[i].c)

    return temp_array
################################################################################################################


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