import pandas as pd
from pandas_datareader import data as pdr
import yfinance as yfin
import yahoo_fin.stock_info as yf

from pyportlib.market_data_sources.base_data_connection import BaseDataConnection
from pyportlib.utils import logger


class YahooConnection(BaseDataConnection):
    _FILE_PREFIX = 'yfin'
    _NAME = 'Yahoo'
    _URL = ''
    yfin.pdr_override()

    def __init__(self):
        super().__init__()

    def __repr__(self):
        return f"{self._NAME} API Connection"

    @property
    def file_prefix(self):
        return self._FILE_PREFIX

    def get_prices(self, ticker: str) -> None:
        """
        Retreives ticker price data and saves .csv file in correct directory

        :param ticker: String Yahoo ticker
        :return:
        """
        filename = f"{self.file_prefix}_{ticker.replace('.TO', '_TO')}_prices.csv"
        directory = self.prices_dir
        ticker = self._convert_ticker(ticker)
        try:
            data = pdr.get_data_yahoo(ticker, progress=False)
        except ValueError:
            logger.logging.error(f"yahoo api error for {ticker}, trying again")
            try:
                data = pdr.get_data_yahoo(ticker, progress=False)
            except ValueError:
                logger.logging.error(f"yahoo api error, no data")
                return
        data.columns = [col.replace(' ', '') for col in data.columns]

        data.to_csv(f"{directory}/{filename}")
        logger.logging.debug(f"{ticker} loaded from yfinance api")

    def get_fx(self, currency_pair: str) -> None:
        """
        Retreives currency pair price data and saves .csv file in correct directory

        :param currency_pair: String
        :return:
        """
        filename = f"{self.file_prefix}_{currency_pair}_fx.csv"
        directory = self.fx_dir

        if currency_pair[:3] == currency_pair[-3:]:
            data = self._make_ptf_currency_df()
        else:
            data = pdr.get_data_yahoo(f'{currency_pair}=X', progress=False)
            data.columns = [col.replace(' ', '') for col in data.columns]

        data.to_csv(f"{directory}/{filename}")
        logger.logging.debug(f"{currency_pair} loaded from yfinance api")

    def get_balance_sheet(self, ticker: str) -> None:
        """
        Retreives balance sheet data and saves .csv file in correct directory
        :param ticker: String Yahoo ticker
        :return:
        """
        filename = f"{self.file_prefix}_{ticker.replace('.TO', '_TO')}_balance_sheet.csv"
        directory = self.statement_dir
        ticker = self._convert_ticker(ticker)
        try:
            bs = yf.get_balance_sheet(ticker)
        except KeyError:
            bs = pd.DataFrame()
        bs.to_csv(f"{directory}/{filename}")
        logger.logging.debug(f"{ticker} balance_sheet loaded from yfinance api")

    def get_cash_flow(self, ticker: str) -> None:
        """
        Retreives cash flow data and saves .csv file in correct directory
        :param ticker: String Yahoo ticker
        :return:
        """
        filename = f"{self.file_prefix}_{ticker.replace('.TO', '_TO')}_cash_flow.csv"
        directory = self.statement_dir
        ticker = self._convert_ticker(ticker)

        try:
            cf = yf.get_cash_flow(ticker)
        except KeyError or TypeError:
            cf = pd.DataFrame()
        cf.to_csv(f"{directory}/{filename}")
        logger.logging.debug(f"{ticker} cash flow loaded from yfinance api")

    def get_income_statement(self, ticker: str) -> None:
        """
        Retreives income statement data and saves .csv file in correct directory
        :param ticker: String Yahoo ticker
        :return:
        """
        filename = f"{self.file_prefix}_{ticker.replace('.TO', '_TO')}_income_statement.csv"
        directory = self.statement_dir
        ticker = self._convert_ticker(ticker)

        try:
            bs = yf.get_cash_flow(ticker)
        except KeyError:
            bs = pd.DataFrame()
        bs.to_csv(f"{directory}/{filename}")
        logger.logging.debug(f"{ticker} income statement loaded from yfinance api")

    def get_dividends(self, ticker: str, start_date=None, end_date=None) -> None:
        """
        Retreives dividends data and saves .csv file in correct directory
        :param ticker: String Yahoo ticker
        :param start_date: Datetime start date
        :param end_date: Datetime end date
        :return:
        """
        filename = f"{self.file_prefix}_{ticker.replace('.TO', '_TO')}_dividends.csv"
        directory = self.statement_dir
        ticker = self._convert_ticker(ticker)
        divs = yf.get_dividends(ticker, start_date=start_date, end_date=end_date, index_as_date=False)
        if divs.empty:
            divs.to_csv(f"{directory}/{filename}")
            logger.logging.debug(f"{ticker} dividends loaded from yfinance api")
        else:
            divs.set_index("date", inplace=True)
            divs.to_csv(f"{directory}/{filename}")
            logger.logging.debug(f"{ticker} dividends loaded from yfinance api")

    def get_splits(self, ticker: str) -> pd.DataFrame:
        """
        Retreives stock splits data
        :param ticker: String Yahoo ticker
        :return:
        """
        ticker = self._convert_ticker(ticker)
        splits = yfin.Ticker(ticker=ticker).get_splits()
        return splits

    @staticmethod
    def _convert_ticker(ticker: str) -> str:
        """
        Convert any type of suffix to yahoo ticker
        :param ticker: Any ticker
        :return:
        """
        ticker = ticker.replace('.TRT', '.TO')
        ticker = ticker.replace(' ', '')
        ticker = ticker.replace('.UN', '-UN')
        ticker = ticker.replace('.VN', '.V')
        ticker = ticker.replace('.B', '-B')
        return ticker
