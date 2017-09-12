from .strategy import Strategy
import numpy

class Combined(Strategy):
    def __init__(self, shift_size=1):
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
        dataframe['mfi'] = self.calc_mfi(dataframe['high'], dataframe['low'],
                dataframe['close'], dataframe['volume'])

        dataframe['middle'] = dataframe['close'].rolling(10).mean()
        std = dataframe['close'].rolling(10).std()
        dataframe['upper'] = dataframe['middle'] + (2 * std)
        dataframe['lower'] = dataframe['middle'] - (2 * std)

        mfi = dataframe['mfi'].values
        close = dataframe['close'].values
        lower = dataframe['lower'].values
        upper = dataframe['upper'].values
        prev_close = dataframe['close'].shift(self.shift_size).values
        prev_mfi = dataframe['mfi'].shift(self.shift_size).values
        prev_lower = dataframe['lower'].shift(self.shift_size).values
        prev_upper = dataframe['upper'].shift(self.shift_size).values
        numpy.seterr(invalid='ignore')
        conditions = [
         ((mfi < 20) & (close >= lower) & (prev_close < prev_lower) &
             (mfi > prev_mfi) & (close < prev_close)),
         ((mfi > 80) & (close <= upper) & (prev_close > prev_upper) &
             (mfi < prev_mfi) & (close > prev_close)),
        ]
        dataframe['signal'] = numpy.select(conditions, [1, -1], default=0)
