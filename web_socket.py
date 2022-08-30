from alpaca_trade_api.rest import REST, TimeFrame
import datetime as dt #to get date
import config
import pytz #to get date
import math #rounding purposes

import logging
from alpaca_trade_api.stream import Stream
from alpaca_trade_api.common import URL #not sure if needed

log = logging.getLogger(__name__)


###########################################################################
###########################################################################
###########################################################################


async def print_trade(t):
    print('trade', t)


async def print_quote(q):
    print('quote', q)


async def print_trade_update(tu):
    print('trade update', tu)


async def print_crypto_trade(t):
    print('crypto trade', t)


def main():
    logging.basicConfig(level=logging.INFO)
    feed = 'iex'  # <- replace to SIP if you have PRO subscription
    stream = Stream(data_feed=feed, raw_data=True, key_id= config.API_KEY, secret_key=config.SECRET_KEY, base_url="https://paper-api.alpaca.markets")
    stream.subscribe_trade_updates(print_trade_update)
    stream.subscribe_trades(print_trade, 'AAPL')
    stream.subscribe_quotes(print_quote, 'IBM')
    #stream.subscribe_crypto_trades(print_crypto_trade, 'BTCUSD')

    @stream.on_bar('MSFT')
    async def _(bar):
        print('bar', bar)

    @stream.on_updated_bar('MSFT')
    async def _(bar):
        print('updated bar', bar)

    @stream.on_status("*")
    async def _(status):
        print('status', status)

    @stream.on_luld('AAPL', 'MSFT')
    async def _(luld):
        print('LULD', luld)

    stream.run()


if __name__ == "__main__":
    main()
