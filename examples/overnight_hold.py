import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import TimeFrame
from alpaca_trade_api.rest_async import gather_with_concurrency, AsyncRest
from alpaca_trade_api.entity_v2 import BarsV2
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

import pandas as pd
import statistics
import sys
import time
import asyncio
from enum import Enum
import pytz

from datetime import datetime, timedelta
from pytz import timezone

stocks_to_hold = 20  # Max 200

# Only stocks with prices in this range will be considered.
max_stock_price = 26
min_stock_price = 6

# API datetimes will match this format. (-04:00 represents the market's TZ.)
api_time_format = '%Y-%m-%dT%H:%M:%S.%f-04:00'

loop = asyncio.get_event_loop()
if sys.argv[1] == 'backtest':
    # so the backtests go faster
    executor = ProcessPoolExecutor(10)
else:
    executor = ProcessPoolExecutor(1)


class DataType(str, Enum):
    Bars = "Bars"
    Trades = "Trades"
    Quotes = "Quotes"


def get_data_method(data_type: DataType):
    if data_type == DataType.Bars:
        return rest.get_bars_async
    elif data_type == DataType.Trades:
        return rest.get_trades_async
    elif data_type == DataType.Quotes:
        return rest.get_quotes_async
    else:
        raise Exception(f"Unsupoported data type: {data_type}")


async def get_historic_data_base(symbols, data_type: DataType, start, end,
                                 timeframe: TimeFrame = None):
    major = sys.version_info.major
    minor = sys.version_info.minor
    if major < 3 or minor < 6:
        raise Exception('asyncio is not support in your python version')
    msg = f"Getting {data_type} data for {len(symbols)} symbols"
    msg += f", timeframe: {timeframe}" if timeframe else ""
    msg += f" between dates: start={start}, end={end}"
    print(msg)
    step_size = 1000
    results = []
    for i in range(0, len(symbols), step_size):
        tasks = []
        for symbol in symbols[i:i + step_size]:
            args = [symbol, start, end, timeframe.value] if timeframe else \
                [symbol, start, end]
            tasks.append(get_data_method(data_type)(*args))

        if minor >= 8:
            results.extend(
                await asyncio.gather(*tasks, return_exceptions=True))
        else:
            results.extend(await gather_with_concurrency(500, *tasks))

    bad_requests = 0
    for response in results:
        if isinstance(response, Exception):
            print(f"Got an error: {response}")
        elif not len(response[1]):
            bad_requests += 1

    print(f"Total of {len(results)} {data_type}, and {bad_requests} "
          f"empty responses.")
    return results


async def get_historic_bars(symbols, start, end, timeframe: TimeFrame):
    return await get_historic_data_base(symbols, DataType.Bars, start, end,
                                        timeframe)


def _process_dataset(dataset, algo_time, start, end, window_size, index):
    if isinstance(dataset, Exception):
        return
    symbol = dataset[0]
    data = dataset[1].truncate(after=end + timedelta(days=1))[
           -window_size:]

    if data.empty or len(data) < window_size:
        return

    # Make sure we aren't missing the most recent data.
    latest_bar = data.iloc[-1].name.to_pydatetime().astimezone(
        timezone('EST'))
    if algo_time:
        gap_from_present = algo_time - latest_bar
        if gap_from_present.days > 1:
            return

    # Now, if the stock is within our target range, rate it.
    price = data.iloc[-1].close
    if price <= max_stock_price and price >= min_stock_price:
        price_change = price - data.iloc[0].close
        # Calculate standard deviation of previous volumes
        volume_stdev = data.iloc[:-1].volume.std()
        if volume_stdev == 0:
            # The data for the stock might be low quality.
            return
        # Then, compare it to the change in volume since yesterday.
        volume_change = data.iloc[-1].volume - data.iloc[-2].volume
        volume_factor = volume_change / volume_stdev
        # Rating = Number of volume standard deviations * momentum.
        rating = price_change / data.iloc[0].close * volume_factor
        if rating > 0:
            return {
                'symbol': symbol,
                'rating': price_change / data.iloc[
                    0].close * volume_factor,
                'price':  price
            }


# Rate stocks based on the volume's deviation from the previous 5 days and
# momentum. Returns a dataframe mapping stock symbols to ratings and prices.
# Note: If algo_time is None, the API's default behavior of the current time
# as `end` will be used. We use this for live trading.
def get_ratings(api, algo_time, datasets=None):
    ratings = pd.DataFrame(columns=['symbol', 'rating', 'price'])
    index = 0
    window_size = 5  # The number of days of data to consider
    formatted_time = None

    if algo_time is not None:
        # Convert the time to something compatable with the Alpaca API.
        start_time = (algo_time.date() -
                      timedelta(days=window_size)).strftime(
            api_time_format)
        formatted_time = algo_time.date().strftime(api_time_format)
        end = pd.Timestamp(formatted_time)
    else:
        end = pytz.timezone("America/New_York").localize(pd.Timestamp('now'))
    start = end - timedelta(
        days=window_size + 10)  # make sure we don't hit weekends

    if not datasets:
        assets = api.list_assets(status="active")
        assets = [asset for asset in assets if asset.tradable]
        symbols = [s.symbol for s in assets]
        snapshot = api.get_snapshots(symbols)
        symbols = list(filter(lambda x: max_stock_price >= snapshot[
            x].latest_trade.p >= min_stock_price if snapshot[x] and snapshot[
            x].latest_trade else False, snapshot))

        datasets = loop.run_until_complete(
            get_historic_bars(symbols, start.isoformat(), end.isoformat(),
                              TimeFrame.Day))
    futures = []
    for dataset in datasets:
        futures.append(executor.submit(_process_dataset, *(
            dataset, algo_time, start, end, window_size, index)))

    done = False
    while not done:
        done = True
        for f in futures:
            if not f.done():
                done = False
                break
        time.sleep(0.1)
    for f in futures:
        res = f.result()
        if res:
            ratings = ratings.append(res, ignore_index=True)

    ratings = ratings.sort_values('rating', ascending=False)
    ratings = ratings.reset_index(drop=True)
    return ratings[:stocks_to_hold]


def get_shares_to_buy(ratings_df, portfolio):
    total_rating = ratings_df['rating'].sum()
    shares = {}
    for _, row in ratings_df.iterrows():
        shares[row['symbol']] = int(
            row['rating'] / total_rating * portfolio / row['price']
        )
    return shares


# Returns a string version of a timestamp compatible with the Alpaca API.
def api_format(dt):
    return dt.strftime(api_time_format)


def backtest(api, days_to_test, portfolio_amount):
    # This is the collection of stocks that will be used for backtesting.
    assets = api.list_assets()
    now = datetime.now(timezone('EST'))
    beginning = now - timedelta(days=days_to_test)

    # The calendars API will let us skip over market holidays and handle early
    # market closures during our backtesting window.
    calendars = api.get_calendar(
        start=beginning.strftime("%Y-%m-%d"),
        end=now.strftime("%Y-%m-%d")
    )
    shares = {}
    cal_index = 0

    assets = api.list_assets(status="active")
    assets = [asset for asset in assets if asset.tradable]
    symbols = [s.symbol for s in assets]
    snapshot = api.get_snapshots(symbols)
    symbols = list(filter(lambda x: max_stock_price >= snapshot[
        x].latest_trade.p >= min_stock_price if snapshot[x] and snapshot[
        x].latest_trade else False, snapshot))

    data = loop.run_until_complete(
        get_historic_bars(
            symbols[:],
            pytz.timezone("America/New_York").localize(
                calendars[0].date - timedelta(days=10)).isoformat(),
            pytz.timezone("America/New_York").localize(
                calendars[-1].date).isoformat(),
            TimeFrame.Day))
    for calendar in calendars:
        # See how much we got back by holding the last day's picks overnight
        portfolio_amount += get_value_of_assets(api, shares, calendar.date)
        print('Portfolio value on {}: {:0.2f} $'.format(calendar.date.strftime(
            '%Y-%m-%d'), portfolio_amount)
        )

        if cal_index == len(calendars) - 2:
            # -2 because we don't have today's data yet
            # We've reached the end of the backtesting window.
            break

        # Get the ratings for a particular day
        ratings = \
            get_ratings(api, timezone('EST').localize(calendar.date),
                        datasets=data)
        shares = get_shares_to_buy(ratings, portfolio_amount)
        for _, row in ratings.iterrows():
            # "Buy" our shares on that day and subtract the cost.
            shares_to_buy = shares[row['symbol']]
            cost = row['price'] * shares_to_buy
            portfolio_amount -= cost
        cal_index += 1

    # Print market (S&P500) return for the time period
    results = loop.run_until_complete(
        get_historic_bars(['SPY'], api_format(calendars[0].date),
                          api_format(calendars[-1].date),
                          TimeFrame.Day))
    sp500_change = (results[0][1].iloc[-1].close - results[0][1].iloc[
        0].close) / results[0][1].iloc[0].close
    print('S&P 500 change during backtesting window: {:.4f}%'.format(
        sp500_change * 100)
    )

    return portfolio_amount


# Used while backtesting to find out how much our portfolio would have been
# worth the day after we bought it.
def get_value_of_assets(api, shares_bought, on_date):
    if len(shares_bought.keys()) == 0:
        return 0

    total_value = 0
    formatted_date = api_format(on_date)

    num_tries = 3
    while num_tries > 0:
        # sometimes it fails so give it a shot few more times
        try:
            barset = loop.run_until_complete(
                get_historic_bars(list(shares_bought.keys()),
                                  pytz.timezone("America/New_York").localize(
                                      on_date).isoformat(),
                                  pytz.timezone("America/New_York").localize(
                                      on_date).isoformat(), TimeFrame.Day))
            barset = dict(barset)
            break
        except Exception as e:
            num_tries -= 1
            if num_tries <= 0:
                print("Error trying to get data")
                sys.exit(-1)
    for symbol in shares_bought:
        df = barset[symbol]
        if not df.empty:
            total_value += shares_bought[symbol] * df.iloc[0].open
    return total_value


def run_live(api):
    # See if we've already bought or sold positions today. If so, we don't want to do it again.
    # Useful in case the script is restarted during market hours.
    bought_today = False
    sold_today = False
    try:
        # The max stocks_to_hold is 200, so we shouldn't see more than 400
        # orders on a given day.
        orders = api.list_orders(
            after=api_format(datetime.today() - timedelta(days=1)),
            limit=400,
            status='all'
        )
        for order in orders:
            if order.side == 'buy':
                bought_today = True
                # This handles an edge case where the script is restarted
                # right before the market closes.
                sold_today = True
                break
            else:
                sold_today = True
    except:
        # We don't have any orders, so we've obviously not done anything today.
        pass
    clock = api.get_clock()
    next_market_time = clock.next_open
    bought_today = False
    sold_today = False
    print_waiting = False
    while True:
        # We'll wait until the market's open to do anything.
        clock = api.get_clock()
        if clock.is_open and not bought_today:
            if sold_today:
                # Wait to buy
                time_until_close = clock.next_close - clock.timestamp
                # We'll buy our shares a couple minutes before market close.
                if time_until_close.seconds <= 120:
                    print('Buying positions...')
                    portfolio_cash = float(api.get_account().cash)
                    ratings = get_ratings(
                        api, None
                    )
                    shares_to_buy = get_shares_to_buy(ratings, portfolio_cash)
                    for symbol in shares_to_buy:
                        if shares_to_buy[symbol] > 0:
                            api.submit_order(
                                symbol=symbol,
                                qty=shares_to_buy[symbol],
                                side='buy',
                                type='market',
                                time_in_force='day'
                            )
                    print('Positions bought.')
                    bought_today = True
            else:
                # We need to sell our old positions before buying new ones.
                time_after_open = pd.Timestamp(
                    clock.timestamp.time().isoformat()) - pd.Timestamp(
                    clock.next_open.time().isoformat())
                # We'll sell our shares just a minute after the market opens.
                if time_after_open.seconds >= 60:
                    print('Liquidating positions.')
                    api.close_all_positions()
                sold_today = True
        else:
            sold_today = False
            if clock.timestamp > next_market_time:
                next_market_time = clock.next_open
                bought_today = False
                sold_today = False
                print("Market Open")
                print_waiting = False
            if not print_waiting:
                print_waiting = True
                print("Waiting for next market day...")
        time.sleep(30)


if __name__ == '__main__':
    api = tradeapi.REST()
    rest = AsyncRest()

    if len(sys.argv) < 2:
        print(
            'Error: please specify a command; either "run" or "backtest '
            '<cash balance> <number of days to test>".')
    else:
        if sys.argv[1] == 'backtest':
            # Run a backtesting session using the provided parameters
            start_value = float(sys.argv[2])
            testing_days = int(sys.argv[3])
            portfolio_value = backtest(api, testing_days, start_value)
            portfolio_change = (portfolio_value - start_value) / start_value
            print('Portfolio change: {:.4f}%'.format(portfolio_change * 100))
        elif sys.argv[1] == 'run':
            run_live(api)
        else:
            print('Error: Unrecognized command ' + sys.argv[1])