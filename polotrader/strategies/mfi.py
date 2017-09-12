from .strategy import Strategy
import numpy

class MFI(Strategy):
    def __init__(self, window_size=4, shift_size=5):
        self.window_size = window_size
        self.shift_size = shift_size
    def calc_mfi(self, highs, lows, closes, volumes):
        typical = (highs + lows + closes) / 3.0
        typical.name = 'typical'
        frame = typical.to_frame()
        frame['rmf'] = typical * volumes
        frame['mfu'] = frame[(frame['typical'] > frame['typical'].shift(1))]['rmf']
        frame['mfd'] = frame[(frame['typical'] < frame['typical'].shift(1))]['rmf']
        frame.fillna(0, inplace=True)
        frame['mfu14'] = frame['mfu'].rolling(14).sum()
        frame['mfd14'] = frame['mfd'].rolling(14).sum()
        frame['mfr'] = frame['mfu14'] / frame['mfd14']
        frame['mfi'] = 100 - (100 / (1 + frame['mfr']))
        return frame['mfi']

    def generate_signals(self, dataframe):
        dataframe['mfi'] = self.calc_mfi(dataframe['high'], dataframe['low'], dataframe['close'], dataframe['volume'])

        numpy.seterr(invalid='ignore')
        mfi = dataframe['mfi'].values
        close = dataframe['close'].values
        prev_close = dataframe['close'].shift(self.shift_size).values
        prev_mfi = dataframe['close'].shift(self.shift_size).values
        conditions = [
         (mfi < 20) & (close < prev_close) & (mfi > prev_mfi),
         ((mfi > 80) & (close > prev_close) &
         (mfi < prev_mfi)),
        ]

        dataframe['signal'] = numpy.select(conditions, [1,-1], default=0)
