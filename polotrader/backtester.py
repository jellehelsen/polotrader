from .exchanges import Poloniex
import pandas

class BackTester(object):
    def __init__(self, pair=('btc', 'eth'), strategy=None, starting_balance=1.0, resolution=14400):
        self.strategy = strategy
        self.pair = pair
        self.exchange = Poloniex()
        self.current_balance = self.starting_balance = starting_balance
        self.alt_balance = 0
        self.resolution = resolution

    def handle_row(self, timestamp, row):
        if row['signal'] == 1 and self.current_balance > 0:
            self.buy(row['open'])
        elif row['signal'] == -1 and self.alt_balance > 0:
            self.sell(row['open'])

    def run(self, start_date, end_date):
        self.get_data(start_date, end_date)
        if self.strategy is not None:
            self.strategy.generate_signals(self.dataframe)
        for row in self.dataframe[(self.dataframe['signal'] != 0)].iterrows():
            self.handle_row(row[0], row[1])
        if self.alt_balance > 0:
            self.sell(self.dataframe.iloc[-1]['close'])

    def get_data(self,start_date, end_date):
        pair = (self.pair[0] + '_' + self.pair[1]).upper()
        json = self.exchange.chart_data(pair, start_date, end_date, resolution=self.resolution)
        dataframe = pandas.DataFrame.from_records(json, index='date')
        dataframe.set_index(pandas.to_datetime(dataframe.index, unit='s'), inplace=True)
        self.dataframe = dataframe

    def buy(self, rate):
        self.alt_balance = self.current_balance / rate
        self.current_balance = 0

    def sell(self, rate):
        self.current_balance = self.alt_balance * rate

if __name__ == '__main__':
    bt = BackTest()
    bt.run('01-01-2017','01-09-2017')
