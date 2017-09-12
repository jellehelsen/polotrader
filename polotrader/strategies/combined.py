from .strategy import Strategy
import talib

class Combined(Strategy):
    def generate_signals(self, dataframe):
        dataframe['mfi'] = talib.MFI(dataframe['high'].values, dataframe['low'].values,
                dataframe['close'].values, dataframe['volume'].values)

        dataframe['upper'], dataframe['middle'], dataframe['lower'] = talib.BBANDS(dataframe['close'].values, timeperiod=50, matype=talib.MA_Type.SMA)
        dataframe['sma10'] = dataframe['close'].rolling(5).mean()
        dataframe['sma100'] = dataframe['close'].rolling(50).mean()
        dataframe['signal'] = 0
        for i in range(len(dataframe)):
            row = dataframe.iloc[i]
            prev_row = dataframe.iloc[i-1]
            if row['close'] >= row['lower'] and prev_row['close'] < prev_row['lower']:
                dataframe.iloc[i,-1] = 1
            elif row['close'] <= row['upper'] and prev_row['close'] > prev_row['upper']:
                dataframe.iloc[i,-1] = -1
            # elif prev_row['mfi'] < 20 and row['mfi'] > prev_row['mfi']:
                # dataframe.iloc[i,-1] = 1
            # elif prev_row['mfi'] > 80 and row['mfi'] < prev_row['mfi']:
                # dataframe.iloc[i,-1] = -1
            # elif row['sma10'] < row['sma100'] and prev_row['sma10'] > prev_row['sma100']:
                # dataframe.iloc[i,-1] = -1
            # elif row['sma10'] > row['sma100'] and prev_row['sma10'] < prev_row['sma100']:
                # dataframe.iloc[i,-1] = 1
