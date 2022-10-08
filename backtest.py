###Template File For backtester


#dependencies
import logging
import alpaca_trade_api as tradeapi #addded line
from config import *
import market_health

from trade import Stock #for try-except blocks


####################################################################################

def backtest(dataset):
    print("test")


#Prints a candlestick chart for the dataset(For a specific Timeframe)
#Candlesticks chart includes the high, low, open, and close values and is represented by a green candle if close > open or red candle if close < open
def print_chart(dataset, timeframe = None):

    if(timeframe == None):
        logging.error("No Timeframe given for backtester in backtest.py printchart()")
    
    #Put Code below to print the chart with labeled axis. Use tradingview.com candlestick chart as reference




##################################################################################################
#### TEST DRIVER #################################################################################
#Test Driver (Temnporary Main Function for backtesting)
def main():
    BASE_URL = "https://paper-api.alpaca.markets"
    api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')

    #Test Data (Dictionary Containing Open, Close, high, and low, time)
    #Pull temp Daily data for test and create temporary stock object
    SPY_STOCK_OBJECT = Stock(name= 'SPY')


    #Daily Test Data
    #Code Below only has closes. Need to make new functiin that does not parse closes
    #DAILY_SPY_CANDLES= market_health.get_Dataset_D(api, SPY_STOCK_OBJECT, DATA_PERIOD = 260)

    #Hourly Test Data
    #HOURLY_SPY_CANDLES= market_health.get_Dataset_IntraDay(api, SPY_STOCK_OBJECT, DATA_PERIOD = 260, temp_timeframe = "Hour")
    #print (HOURLY_SPY_CANDLES)

    backtest(dataset = DAILY_SPY_CANDLES)


main()