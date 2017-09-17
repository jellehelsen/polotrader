from .strategy import Strategy
import numpy

class Bollinger(Strategy):
    def __init__(self, window_size=10):
        self.window_size = window_size

    def generate_signals(self, dataframe):
        dataframe['middle'] = dataframe['close'].rolling(self.window_size).mean()
        std = dataframe['close'].rolling(self.window_size).std()
        dataframe['upper'] = dataframe['middle'] + (2 * std)
        dataframe['lower'] = dataframe['middle'] - (2 * std)

        close = dataframe['close'].values
        lower = dataframe['lower'].values
        upper = dataframe['upper'].values
        prev_close = dataframe['close'].shift(1).values
        prev_lower = dataframe['lower'].shift(1).values
        prev_upper = dataframe['upper'].shift(1).values

        numpy.seterr(invalid='ignore')

        conditions = [
         ((close >= lower) & (prev_close < prev_lower)),
         ((close <= upper) & (prev_close > prev_upper)),
        ]
        dataframe['signal'] = numpy.select(conditions, [1, -1], default=0)
