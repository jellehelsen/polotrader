from .exchange import Exchange
from pandas import DataFrame as df, read_json
from urllib.parse import urlencode
import hmac
from hashlib import sha512
from time import time, sleep, mktime, strptime
from decimal import *
from datetime import datetime, timedelta
from functools import reduce

def createTimeStamp(datestr, format='%d-%m-%Y'):
    return int(mktime(strptime(datestr, format)))

class Poloniex(Exchange):
    base_uri = 'https://poloniex.com'
    def trading_request(self, command, params={}):
        self.logger.debug("%s: %s: %s" % (type(self).__name__, command, params))
        params['command'] = command
        params['nonce'] = int(time()*1000)
        query = bytes(urlencode(params), 'utf-8')
        sign = hmac.new(self.secret, query, sha512).hexdigest()
        headers = {'Key': self.api_key, 'Sign': sign}
        result = self.post('/tradingApi', headers=headers, data=params)
        self.logger.debug(result.text)
        return result

    def balance(self, coin):
        return float(self.trading_request("returnBalances").json()[coin])

    def addresses(self):
        return self.trading_request('returnDepositAddresses').json()

    def address(self, coin):
        existing_addresses = self.addresses()
        if coin in existing_addresses:
            return existing_addresses[coin]
        else:
            return self.trading_request('generateNewAddress', {'currency': coin}).json()['response']

    def withdraw(self, coin, amount, address):
        result = self.trading_request('withdraw', {'currency': coin, 'amount': amount, 'address': address}).json()
        return amount-self.withdraw_fee(coin)

    def open_orders(self, pair=None, order_number=None):
        pair = pair or 'all'
        result = self.trading_request('returnOpenOrders', { 'currencyPair': pair.replace('/','_') }).json()
        if order_number:
            return list(filter(lambda x: int(x['orderNumber']) == int(order_number), result))
        else:
            return result

    def trade_history(self, pair=None, order_number=None):
        pair = pair or 'all'
        result = self.trading_request('returnTradeHistory',\
                {'currencyPair': pair.replace('/','_')}).json()
        if order_number:
            return list(filter(lambda x: int(x['orderNumber']) == int(order_number), result))
        else:
            return result

    def withdraw_fee(self, coin):
        return float(self.coin_info()[coin]['txFee'])

    def min_withdraw_amount(self, coin):
        pass

    def without_fee(self, order):
        amount = Decimal(order['amount'])
        fee    = Decimal(order['fee'])
        significant_digits = len(str(int(amount)))
        getcontext().prec=8+significant_digits
        getcontext().rounding = ROUND_UP
        return float(amount-(amount*fee))

    def buy(self, pair, amount, rate, wait=False):
        result = self.trading_request('buy',\
                {'currencyPair': pair.replace('/','_'), 'rate': rate, 'amount': amount}).json()
        if wait:
            order_number = result['orderNumber']
            while len(self.open_orders(pair, order_number)) > 0:
                sleep(10)
            history = self.trade_history(pair, order_number)
            # import code
            # code.interact(local=locals())
            return reduce(lambda a, b: a + self.without_fee(b), history, 0)
        return reduce(lambda a, b: a + float(b['amount']), result['resultingTrades'], 0)

    def sell(self, pair, amount, rate):
        return self.trading_request('sell', {'currencyPair': pair.replace('/','_'), 'rate': rate, 'amount': amount}).json()

    def ticker(self, column=None):
        response = self.get("/public?command=returnTicker")
        df_tmp = read_json(response.text, orient='index')
        index = df_tmp.index.str.replace('_','/')
        if column is None:
            return df_tmp.rename(columns=self.columns_mapping()).set_index(index)
        return df(df_tmp.rename(columns=self.columns_mapping())[column])\
                .set_index(index)

    def chart_data(self, pair, start_date, end_date, resolution=14400):
        params = {'command': 'returnChartData', 'currencyPair': pair}
        params['start'] = createTimeStamp(start_date)
        params['end'] = createTimeStamp(end_date)
        params['period'] = resolution
        return self.get('/public?%s' % urlencode(params)).json()

    def chart_data2(self, pair, start_date, end_date, resolution=14400):
        params = {'command': 'returnChartData', 'currencyPair': pair}
        params['start'] = start_date
        params['end'] = end_date
        params['period'] = resolution
        return self.get('/public?%s' % urlencode(params)).json()

    def coin_info(self):
        if self._coin_info == None:
            self._coin_info = self.get('/public?command=returnCurrencies').json()
        return self._coin_info

    def columns_mapping(self):
        return {'lowestAsk': 'min_ask', 'highestBid': 'max_bid'}
