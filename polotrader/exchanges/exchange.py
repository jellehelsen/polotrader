import requests as r
from pandas import DataFrame as df, read_json
import logging

class Exchange(object):
    def __init__(self, api_key=None, secret=None, logger=None):
        self.api_key = api_key
        self.secret = secret
        self._coin_info = None
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger('arbitrage_bot')
            handler = logging.StreamHandler()
            formatter = logging.Formatter(\
                    '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def get(self, url, headers={}):
        return r.get(self.base_uri + url, headers=headers)

    def post(self, url, headers={}, data={}):
        return r.post(self.base_uri + url, headers=headers, data=data)

