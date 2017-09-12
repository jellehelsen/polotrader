import time
import pandas
import warnings
from exchanges import Poloniex
from strategies import *
class Bot(object):
    def __init__(self, pair=('btc','eth'), strategy=None, api_key=None, api_secret=None, resolution=300):
        self.pair = pair
        self.strategy = strategy
        if api_key is None:
            warnings.warn("No api key given! No trades can occur!")
        elif api_secret is None:
            warnings.warn("No api secret given! No trades can occur!")
        self.exchange = Poloniex(api_key, api_secret)
        self.resolution = resolution

    def get_data(self):
        pair = (self.pair[0] + '_' + self.pair[1]).upper()
        end = int(time.mktime(time.gmtime())+86400)
        start = int(time.mktime(time.gmtime())-86400)
        json = self.exchange.chart_data2(pair, start, end, resolution=self.resolution)
        dataframe = pandas.DataFrame.from_records(json, index='date')
        dataframe.set_index(pandas.to_datetime(dataframe.index, unit='s'), inplace=True)
        self.dataframe = dataframe
        if self.strategy is not None:
            self.strategy.generate_signals(self.dataframe)

    def run(self):
        self.get_data()
        last_ts = self.dataframe.iloc[-1].name
        while time.mktime(last_ts.timetuple()) < (time.mktime(time.gmtime()) - 300000):
            print(last_ts, time.mktime(last_ts.timetuple()), (time.mktime(time.gmtime()) - 300000))
            time.sleep(10)
            self.get_data()
            last_ts = bot.dataframe.iloc[-1].name

        if self.dataframe.iloc[-1]['signal'] == -1:
            self.sell()
        elif self.dataframe.iloc[-1]['signal'] == 1:
            self.buy()

    def buy(self):
        balance = self.exchange.balance(self.pair[0])
        if balance > 0.001:
            rate = self.dataframe.iloc[-1]['close']
            amount_to_buy = balance / rate
            pair = (self.pair[0] + '_' + self.pair[1]).upper()
            print("Buying {} {} at {}".format(amount_to_buy, self.pair[1], rate))
            self.exchange.buy(pair, amount_to_buy, rate)

    def sell(self):
        balance = self.exchange.balance(self.pair[1])
        if balance > 0.001:
            rate = self.dataframe.iloc[-1]['close']
            pair = (self.pair[0] + '_' + self.pair[1]).upper()
            print("Selling {} {} at {}".format(balance, self.pair[1], rate))
            self.exchange.buy(pair, balance, rate)


if __name__ == '__main__':
    import os
    api_key = os.getenv('POLONIEX_API_KEY')
    api_secret = os.getenv('POLONIEX_API_SECRET')
    coin = os.getenv("POLOBOT_COIN", 'eth')
    shift_width = os.getenv("POLOBOT_SHIFTWIDTH", 1)
    bot = Bot(strategy=Combined(shift_size=int(shift_width)), pair=('btc', coin), api_key=api_key, api_secret=api_secret)
    bot.run()
