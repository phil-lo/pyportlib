from typing import List, Set

from pyportlib.services.data_reader import DataReader
from pyportlib.utils import logger


class FxRates:
    _NAME = "FX Rates"

    def __init__(self, ptf_currency: str, currencies: Set[str], datareader: DataReader):
        self.pairs = [f"{curr}{ptf_currency}" for curr in currencies]
        self.rates = {}
        self.datareader = datareader
        self.ptf_currency = ptf_currency
        self._load()

    def __repr__(self):
        return self._NAME

    def set_pairs(self, pairs: List[str]):
        self.pairs = pairs
        self.refresh()

    def reset(self):
        self.pairs = []
        self.rates = {}
        self._load()

    def refresh(self):
        """
        Updates the objects
        :return:
        """
        for pair in self.pairs:
            self.datareader.update_fx(currency_pair=pair)
        self._load()

    def get(self, pair: str):
        """
        Retreives currency pair data. If pair is missing, it will be added.
        :param pair:
        :return:
        """
        if len(pair) != 6:
            logger.logging.error(f'{pair} is not a valid pair, enter valid currency pair')

        if pair not in self.pairs and not self.pairs:
            self.set_pairs([pair])
            logger.logging.debug(f'setting pairs')
        elif pair not in self.pairs:
            self.pairs.append(pair)
            self._load()

        return self.rates.get(pair)

    def _load(self):
        for pair in self.pairs:
            self.rates[pair] = self.datareader.read_fx(currency_pair=pair)
        logger.logging.debug(f'fx rates loaded')
