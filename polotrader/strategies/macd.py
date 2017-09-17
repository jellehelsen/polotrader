from .strategy import Strategy
import numpy

class MACD(Strategy):
    def generate_signals(self, dataframe):
        pass
        dataframe['ema12'] = dataframe['close'].ewm(12).mean()
        dataframe['ema26'] = dataframe['close'].ewm(26).mean()
        dataframe['macd']  = dataframe['ema12'] - dataframe['ema26']
        dataframe['sline'] = dataframe['macd'].ewm(9).mean()
        dataframe['mach']  = dataframe['macd'] - dataframe['sline']

        macd = dataframe['mach'].values
        prev_macd= dataframe['mach'].shift(1).values

        numpy.seterr(invalid='ignore')
        conditions = [
                ((macd < 0) & (macd > -0.2)),
                ((macd < 0) & (macd < 0.2)),
                ]
        dataframe['signal'] = numpy.select(conditions, [1, -1], default=0)

