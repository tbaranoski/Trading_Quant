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
#api_test = REST()
#import alpaca_trad_api #delete

#Constants
LONG_DISTRIBUTION = 25
SHORT_DISTRIBUTION =  7
PERCENT_TO_BE_DISTRIBUTION = -.2

#############################################################################################################################################
##Returns Distribution Day Count
def get_Distribution_DAY_COUNT(NUM_DAYS, TICKER_D_BARS):
    distribution_days = 0

    for i in range (NUM_DAYS):
        #Calculate percentage chnage from yesterdays close
        change_percent = ((((TICKER_D_BARS[NUM_DAYS - i-1].c) - (TICKER_D_BARS[NUM_DAYS - i-2].c)) / (TICKER_D_BARS[NUM_DAYS - i-1].c))) * 100
        #print("Change %: ", change_percent)

        # IF index dropped by more than .2% look at volume comparison between yesterday and today
        if(change_percent <= PERCENT_TO_BE_DISTRIBUTION):
            if((TICKER_D_BARS[NUM_DAYS - i-1].v - (TICKER_D_BARS[NUM_DAYS - i-2].c)) > 0):                
                distribution_days = distribution_days + 1

    return distribution_days
#############################################################################################################################################

##Returns SHORT Term Distribution Day Count (Last 7 DAYS) for Major Indexes:
#$SPY, $QQQ, $DIA, $IWO, $IWM

##Returns whether Major Indexes are above 21EMA and 9 EMA
##$SPY, $QQQ, $DIA, $IWO, $IWM

##Calculate Scores


#Main function in file
def get_Market_health(api):
    
    #Calculate start_time since get_bars works in reverse for get_bars (V2 endpoint)
    #Reference https://forum.alpaca.markets/t/get-bars-vs-get-barset/8127/6
    timeNow = dt.datetime.now(pytz.timezone('US/Eastern'))
    start_time_long_distribution = timeNow - dt.timedelta(days=LONG_DISTRIBUTION)
    start_time_short_distribution = timeNow - dt.timedelta(days=SHORT_DISTRIBUTION)

    #Get data for SPY and QQQ


    SPY_D_BARSET_LONG = api.get_bars('SPY', TimeFrame.Day, start = start_time_long_distribution.isoformat(), end = None, limit = LONG_DISTRIBUTION)
    #SPY_D_BARS_LONG = SPY_D_BARSET_LONG['SPY']

    SPY_D_BARSET_SHORT = api.get_bars('SPY', TimeFrame.Day, start = start_time_short_distribution.isoformat(), end = None, limit = SHORT_DISTRIBUTION)
    #SPY_D_BARS_SHORT = SPY_D_BARSET_SHORT['SPY']

    QQQ_D_BARSET_LONG = api.get_bars('QQQ', TimeFrame.Day, start = start_time_long_distribution.isoformat(), end = None, limit = LONG_DISTRIBUTION)
    #QQQ_D_BARS_LONG = QQQ_D_BARSET_LONG['QQQ']

    QQQ_D_BARSET_SHORT = api.get_bars('QQQ', TimeFrame.Day, start = start_time_short_distribution.isoformat(), end = None, limit = SHORT_DISTRIBUTION)
    #QQQ_D_BARS_SHORT = QQQ_D_BARSET_SHORT['QQQ']


    #Calculate distribution days
    SPY_DIST_LONG = get_Distribution_DAY_COUNT(LONG_DISTRIBUTION, SPY_D_BARSET_LONG)
    #SPY_DIST_SHORT = get_Distribution_DAY_COUNT(SHORT_DISTRIBUTION, SPY_D_BARS_SHORT)
    #QQQ_DIST_LONG = get_Distribution_DAY_COUNT(LONG_DISTRIBUTION, QQQ_D_BARS_LONG)
    #QQQ_DIST_SHORT = get_Distribution_DAY_COUNT(SHORT_DISTRIBUTION, QQQ_D_BARS_SHORT)

    print("test print: ", SPY_DIST_LONG)