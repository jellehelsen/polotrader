from .strategy import Strategy

class BuyAndHold(Strategy):
    def generate_signals(self, dataframe):
        dataframe['signal'] = 0
        dataframe.ix[0, 'signal'] = 1
        dataframe.ix[-1, 'signal'] = -1
