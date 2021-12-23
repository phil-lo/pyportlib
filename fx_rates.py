from datetime import datetime
from typing import List, Union

import pandas as pd

from data_sources.data_reader import DataReader
from utils import logger
from utils.dates_utils import get_market_days


class FxRates:
    def __init__(self, ptf_currency: str, currencies: List[str]):
        self.pairs = [f"{curr}{ptf_currency}" for curr in currencies]
        self.rates = {}
        self.datareader = DataReader()
        self.ptf_currency = ptf_currency
        self._load()

    def set(self, pairs: List[str]):
        self.pairs = pairs
        self._load()

    def refresh(self):
        for pair in self.pairs:
            self.datareader.update_fx(currency_pair=pair)
        self._load()

    def get(self, pair: str):
        if len(pair) != 6:
            logger.logging.error('enter valid currency pair')
        return self.rates.get(pair)

    def _load(self):
        for pair in self.pairs:
            self.rates[pair] = self.datareader.read_fx(currency_pair=pair)
        logger.logging.info(f'fx rates loaded')

