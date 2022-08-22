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
#To account for Sunday and Saturday which are not actual tradin days. + 10 accounts for any holidays
LONG_DISTRIBUTION = math.ceil((LONG_DISTRIBUTION_NUMBER *((9/7)) + 10))
print("The Long distribution is: ", LONG_DISTRIBUTION)
SHORT_DISTRIBUTION =  math.ceil((SHORT_DISTRIBUTION_NUMBER *((9/7)) + 10))

#############################################################################################################################################

#FOR TESTING
def print_Close(NUM_DAYS, TICKER_D_BARS):
    lenght_data = len(TICKER_D_BARS)
    for i in range (lenght_data):
        print("Index: ", i, "Date: ", TICKER_D_BARS[i].t, "Close: ", TICKER_D_BARS[i].c )


##Returns Distribution Day Count
def get_Distribution_DAY_COUNT(NUM_DAYS, TICKER_D_BARS):
    distribution_days = 0

    #Get Start Index
    start_index = (len(TICKER_D_BARS)) - NUM_DAYS
    end_index = (len(TICKER_D_BARS)) - 1
    print (start_index)
    print (end_index)


    for i in range (start_index, end_index):
        #Calculate percentage chnage from yesterdays close
        change_percent = ((((TICKER_D_BARS[i+1].c) - (TICKER_D_BARS[i].c)) / (TICKER_D_BARS[i].c))) * 100
        #print("Change %: ", change_percent, "Close is: ", TICKER_D_BARS[i].c, "Date is: ", TICKER_D_BARS[i].t)

        # IF index dropped by more than .2% look at volume comparison between yesterday and today
        if(change_percent <= PERCENT_TO_BE_DISTRIBUTION):
            if((TICKER_D_BARS[i+1].v - (TICKER_D_BARS[i].v)) > 0):                
                distribution_days = distribution_days + 1
                #print("Distribution Day\n")

    return distribution_days
#############################################################################################################################################
#Main function in file
def get_Market_health(api):
    
    ###################################################################################
    ###################################################################################
    #calculate Distribution Day Count For Major Indexes ($SPY, $QQQ, $DIA, $IWO, $IWM)
    # over a longer period (currentlly lsast 25 days) and over a shorter period (last 7 days)
    ###################################################################################
    ###################################################################################

    #Calculate start_time since get_bars works in reverse for get_bars (V2 endpoint)
    #Reference https://forum.alpaca.markets/t/get-bars-vs-get-barset/8127/6
    timeNow = dt.datetime.now(pytz.timezone('US/Eastern'))
    print("\n\nThe time now is: ", timeNow)

    start_time_long_distribution = timeNow - dt.timedelta(days=LONG_DISTRIBUTION)
    start_time_short_distribution = timeNow - dt.timedelta(days=SHORT_DISTRIBUTION)

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

    #Print Distribution Days
    print("Distribution Day Count($SPY) over last",LONG_DISTRIBUTION_NUMBER, " days: ", SPY_DIST_LONG)
    print("Distribution Day Count($SPY) over last",SHORT_DISTRIBUTION_NUMBER, " days: ", SPY_DIST_SHORT)
    print("Distribution Day Count($QQQ) over last",LONG_DISTRIBUTION_NUMBER, " days: ", QQQ_DIST_LONG)
    print("Distribution Day Count($QQQ) over last",SHORT_DISTRIBUTION_NUMBER, " days: ", QQQ_DIST_SHORT)
    print("Distribution Day Count($DIA) over last",LONG_DISTRIBUTION_NUMBER, " days: ", DIA_DIST_LONG)
    print("Distribution Day Count($DIA) over last",SHORT_DISTRIBUTION_NUMBER, " days: ", DIA_DIST_SHORT)
    print("Distribution Day Count($IWO) over last",LONG_DISTRIBUTION_NUMBER, " days: ", IWO_DIST_LONG)
    print("Distribution Day Count($IWO) over last",SHORT_DISTRIBUTION_NUMBER, " days: ", IWO_DIST_SHORT)
    print("Distribution Day Count($IWM) over last",LONG_DISTRIBUTION_NUMBER, " days: ", IWM_DIST_LONG)
    print("Distribution Day Count($IWM) over last",SHORT_DISTRIBUTION_NUMBER, " days: ", IWM_DIST_SHORT)

    #def print_distribution_day