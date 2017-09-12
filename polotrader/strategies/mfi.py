from .strategy import Strategy
import numpy

class MFI(Strategy):
    def calc_smi(self, highs, lows, closes, volumes):
        pass
        typical = (highs + lows + closes) / 3.0
        raw_money_flow = typical * volumes

    def generate_signals(self, dataframe):
        dataframe['typical'] = (dataframe['high'] + dataframe['low'] + dataframe['close']) / 3.0
        dataframe['rmf'] = dataframe['typical'] * dataframe['volume']

        dataframe['mfu14'] = 0
        dataframe['mgd14'] = 0
        dataframe['mfu'] = 0
        dataframe['mfd'] = 0
        dataframe['mfi'] = numpy.nan
        dataframe['signal'] = 0
        for i in range(len(dataframe)):
            row = dataframe.iloc[i]
            prev_row = dataframe.iloc[i-1]

            if row['typical'] > prev_row['typical']:
                dataframe.iloc[i, -4] = row['rmf']
            if row['typical'] < prev_row['typical']:
                dataframe.iloc[i, -3] = row['rmf']
            if i > 14:
                mfu = dataframe.iloc[i-13:i+1, -4].sum()
                mfd = dataframe.iloc[i-13:i+1, -3].sum()
                dataframe.iloc[i,-6] = mfu
                dataframe.iloc[i,-5] = mfd
                # if mfd == 0.0:
                    # mfd = 1e-6
                mfr = mfu/mfd
                dataframe.iloc[i, -2] = 100 - 100 / (1 + mfr)
            row = dataframe.iloc[i]
            prev_row = dataframe.iloc[i-1]
            if row['mfi'] < 20 and row['mfi'] > prev_row['mfi']:
                dataframe.iloc[i,-1] = 1
            elif row['mfi'] > 80 and row['mfi'] < prev_row['mfi']:
                dataframe.iloc[i,-1] = -1

