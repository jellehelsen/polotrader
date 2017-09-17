from .strategy import Strategy
import numpy

class EMA(Strategy):
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
        dataframe['ema10'] = dataframe['close'].ewm(10).mean()
        dataframe['ema40'] = dataframe['close'].ewm(40).mean()
        dataframe['mfi'] = self.calc_mfi(dataframe['high'], dataframe['low'], dataframe['close'], dataframe['volume'])

        ema10 = dataframe['ema10'].values
        ema40 = dataframe['ema40'].values
        mfi   = dataframe['mfi'].values

        prev_ema10 = dataframe['ema10'].shift(1).values
        prev_ema40 = dataframe['ema40'].shift(1).values

        numpy.seterr(invalid='ignore')

        conditions = [
                ((mfi < 20) & (ema10 > ema40) & (prev_ema10 < prev_ema40)),
                ((mfi > 80) & (ema10 < ema40) & (prev_ema10 > prev_ema40)),
                ]
        dataframe['signal'] = numpy.select(conditions, [1, -1], default=0)
