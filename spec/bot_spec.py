from polotrader.bot import Bot
from polotrader.exchanges import *
from polotrader.strategies import Strategy
from robber import expect
from mock import patch, Mock
from doublex import Spy, method_returning, when, ANY_ARG, assert_that, called
from hamcrest import *
from pandas import DataFrame
import warnings
import time

with description('bot'):
    with context("interaction with exchange"):
        with before.each:
            self.mock_exchange = Spy(Poloniex())
            with patch('polotrader.bot.Poloniex', Mock(return_value=self.mock_exchange)):
                self.subject = Bot(api_key='key',api_secret='secret')
        with it("should use the mock exchange"):
            expect(self.subject.exchange).to.eq(self.mock_exchange)
        with context("get_data"):
            with before.each:
                self.timestamp = int(time.time())
                when(self.mock_exchange).chart_data2(ANY_ARG).returns([{'date': self.timestamp}])
            with it('should get the chart_data'):
                self.subject.get_data()
                assert_that(self.mock_exchange.chart_data2, called())
            with it("should set the dataframe"):
                self.subject.get_data()
                assert_that(self.subject.dataframe, instance_of(DataFrame) )
                assert_that(int(time.mktime(self.subject.dataframe.index[0].timetuple()) - time.timezone),
                        equal_to(self.timestamp))

            with it("should generate the signals"):
                strategy = Spy(Strategy)
                self.subject.strategy = strategy
                self.subject.get_data()
                assert_that(strategy.generate_signals, called())
