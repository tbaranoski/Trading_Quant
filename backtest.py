###Template File For backtester


#dependencies
import logging
import alpaca_trade_api as tradeapi #addded line
from config import *
import market_health
import datetime as dt #to get date
from alpaca_trade_api.rest import REST, TimeFrame
import pytz #to get date

from trade import Stock #for try-except blocks


####################################################################################

#Prints a candlestick chart for the dataset(For a specific Timeframe)
#Candlesticks chart includes the high, low, open, and close values and is represented by a green candle if close > open or red candle if close < open
def print_chart(dataset = None, timeframe = None):

    if(timeframe == None):
        logging.error("No Timeframe given for backtester in backtest.py printchart()")
    
    #Put Code below to print the chart with labeled axis. Use tradingview.com candlestick chart as reference
    
    #Print Daily Chart
    elif(timeframe == "Day"):
        print(" ")

    #Print intraday chart
    else:
        print(" ")




##################################################################################################
#### TEST DRIVER #################################################################################
#Test Driver (Temnporary Main Function for backtesting)
def main():
    BASE_URL = "https://paper-api.alpaca.markets"
    api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')

    #Test Data (Dictionary Containing Open, Close, high, and low, time)
    #Pull temp Daily data for test and create temporary stock object
    SPY_STOCK_OBJECT = Stock(name= 'SPY')

    timeNow = dt.datetime.now(pytz.timezone('US/Eastern'))
    start_time = timeNow - dt.timedelta(days=400)
    start_time_hour = timeNow - dt.timedelta(days=35)

    DAILY_SPY_CANDLES = api.get_bars(SPY_STOCK_OBJECT.name, TimeFrame.Day, start = start_time.isoformat(), end = None)
    HOURLY_SPY_CANDLES = api.get_bars(SPY_STOCK_OBJECT.name, TimeFrame.Hour, start = start_time_hour.isoformat(), end = None)

    #Make Artificial Array with States
    state_array_Daily = [7] * len(DAILY_SPY_CANDLES)
    state_array_Hourly = [7] * len(HOURLY_SPY_CANDLES)
    
    print(state_array_Daily)

    #Test 1 : Daily Timeframe
    #print("Test 1...\n\n")
    #print_chart(dataset = DAILY_SPY_CANDLES, timeframe = "Day")


    #Test 2: Intraday TImeframes
    #print("Test 2...\n\n")
    #print_chart(dataset = HOURLY_SPY_CANDLES, timeframe = "Hour")


main()