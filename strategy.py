
from enum import Enum
import logging 

#Marks the strategy to use (going LONG or selling SHORT) in the Stock Object
def trade_basic(api, group):
    
    #Determine which stock in the group are suitbale for going LONG or SHORTING and save as attribute in Stock class
    for stock_obj in group.stock_objects_array:

        #If EMA are stacked positive (9EMA above 21 EMA on Daily) consider LONG trades and price is above 21 EMA
        if((stock_obj.EMA_9 > stock_obj.EMA_21) and (stock_obj.current_price_estimate > stock_obj.EMA_21)):

            #If the trend on daily chart is in state1(Confirmed Uptrend) or state 4 (possible downtrend reversal)
            if((stock_obj.trend.trend_child_Day.value == 1) or (stock_obj.trend.trend_child_Day.value == 4)):
                
                #If one minute chart is in state1(Confirmed Uptrend) or state 4 (possible downtrend reversal) buy the stock
                if((stock_obj.trend.trend_child_1min.value == 1) or (stock_obj.trend.trend_child_1min.value == 4)):    

                    #Mark the strategy as LONG
                    stock_obj.strategy = "LONG"

        #If EMA are stacked negative on daily (9EMA below 21 EMA on Daily) consider SHORT trades and price is below 21 EMA
        elif((stock_obj.EMA_9 < stock_obj.EMA_21) and (stock_obj.current_price_estimate < stock_obj.EMA_21)):
             
            #If the trend on daily chart is in state3(Confirmed Downtrend) or state 2 (possible uptrend reversal)
            if((stock_obj.trend.trend_child_Day.value == 3) or (stock_obj.trend.trend_child_Day.value == 2)):
                
                #If one minute chart is in state1(Confirmed Uptrend) or state 4 (possible downtrend reversal) buy the stock
                if((stock_obj.trend.trend_child_1min.value == 3) or (stock_obj.trend.trend_child_1min.value == 4)):    

                    #Mark the strategy as SHORT
                    stock_obj.strategy = "SHORT"
    
