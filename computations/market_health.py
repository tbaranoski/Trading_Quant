#### The Purpose of this file is to look at Market Internals and Metrics which determine the health of the trend.
#### The file will return different scores which will then be used when managing the portfolio. 

#### Low Scores: Suggest trimming profitable positions into strength(2-3 ATR from 21 EMA), cutting low Relative strength stocks
#### and becoming more picky with future entries for the short term. (A bigger emphasis on TML (True Market Leaders) and heavy volume breakouts)

#### High scores: Suggest Positions can be swung for longer, portfolio exposure can increase if some of psoitions are in profit and stop-loss gets move up.
####: Less picky on future entries with the focus on stocks form the leading sectors.

##Distribution Day: A day where market index drops by more than .2% with greater volume than the day before. Indicates Institutional selling AKA Distribution.
##########################################################################################################################################################
import alpaca_trade_api as tradeapi

#Constants
LONG_DISTRIBUTION = 25
SHORT_DISTRIBUTION =  7
PERCENT_TO_BE_DISTRIBUTION = -.2

#############################################################################################################################################
##Returns Long Term Distribution Day Count (Last 25 DAYS) for Major Indexes:
#$SPY, $QQQ, $DIA, $IWO, $IWM
def get_Distribution_DAY_COUNT(NUM_DAYS, TICKER_D_BARS):
    distribution_days = 0

    for i in range (NUM_DAYS):
        #Calculate percentage chnage from yesterdays close
        change_percent = ((((TICKER_D_BARS[NUM_DAYS - i-1].c) - (TICKER_D_BARS[NUM_DAYS - i-2].c)) / (TICKER_D_BARS[NUM_DAYS - i-1].c))) * 100
        #print("Change %: ", change_percent)

        # IF index dropped by more than 2% look at volume comparison between yesterday and today
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


def get_Market_health(api):
    #MAIN()
    SPY_D_BARSET_LONG = api.get_barset('SPY', 'day', limit = LONG_DISTRIBUTION)
    SPY_D_BARS_LONG = SPY_D_BARSET_LONG['SPY']

    SPY_D_BARSET_SHORT = api.get_barset('SPY', 'day', limit = SHORT_DISTRIBUTION)
    SPY_D_BARS_SHORT = SPY_D_BARSET_SHORT['SPY']

    QQQ_D_BARSET_LONG = api.get_barset('QQQ', 'day', limit = LONG_DISTRIBUTION)
    QQQ_D_BARS_LONG = QQQ_D_BARSET_LONG['QQQ']

    QQQ_D_BARSET_SHORT = api.get_barset('QQQ', 'day', limit = SHORT_DISTRIBUTION)
    QQQ_D_BARS_SHORT = QQQ_D_BARSET_SHORT['QQQ']




    SPY_DIST_LONG = get_Distribution_DAY_COUNT(LONG_DISTRIBUTION, SPY_D_BARS_LONG)
    SPY_DIST_SHORT = get_Distribution_DAY_COUNT(SHORT_DISTRIBUTION, SPY_D_BARS_SHORT)
    QQQ_DIST_LONG = get_Distribution_DAY_COUNT(LONG_DISTRIBUTION, QQQ_D_BARS_LONG)
    QQQ_DIST_SHORT = get_Distribution_DAY_COUNT(SHORT_DISTRIBUTION, QQQ_D_BARS_SHORT)
