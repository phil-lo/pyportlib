from datetime import datetime
import pandas as pd

from pyportlib.market_data_sources.base_data_connection import BaseDataConnection
from pyportlib.utils import logger, files_utils


class DataReader:
    NAME = 'Data Reader'

    def __init__(self, market_data_source: BaseDataConnection, statements_data_source: BaseDataConnection):
        self._market_data_source = market_data_source
        self._statements_data_source = statements_data_source

    def __repr__(self):
        return self.NAME

    def read_prices(self, ticker: str) -> pd.Series:
        """
        Read prices saved locally in client data folder.
        If no .csv found, prices will be fetched with the data source

        :param ticker: Stock ticker
        :return:
        """
        directory = self._market_data_source.prices_dir
        filename = f"{self._market_data_source.file_prefix}_{ticker.replace('.TO', '_TO')}_prices.csv"

        if files_utils.check_file(directory=directory,
                                  file=filename):
            df = pd.read_csv(f"{directory}/{filename}")
            df = df.set_index('Date').dropna()
            df.index = pd.to_datetime(df.index)

            return df['Close']
        else:
            logger.logging.info(f'no price data to read for {ticker}, fetching new data from api')
            self.update_prices(ticker=ticker)
            return self.read_prices(ticker)

    def read_fx(self, currency_pair: str) -> pd.Series:
        """
        Read fx rates saved locally in client data folder.
        If no .csv found, rates will be fetched

        :param currency_pair: Fx pair ex. USDCAD or CADUSD
        :return:
        """
        directory = self._market_data_source.fx_dir
        filename = f"{self._market_data_source.file_prefix}_{currency_pair}_fx.csv"

        if files_utils.check_file(directory=directory,
                                  file=filename):
            df = pd.read_csv(f"{directory}/{filename}")
            df = df.set_index('Date')
            df.index = pd.to_datetime(df.index)
            return df['Close']
        else:
            logger.logging.info(f'no fx data to read for {currency_pair}, fetching new data from api')
            self.update_fx(currency_pair=currency_pair)
            return self.read_fx(currency_pair)

    def read_fundamentals(self, ticker: str, statement_type: str) -> pd.DataFrame:
        """
        Read statements saved locally in client data folder.
        If no .csv found, statements will be fetched

        :param ticker: Stock ticker to read fundamentals data from
        :param statement_type: Choose from ('balance_sheet', 'cashflow', 'income_statement')
        :return: Dataframe with statement data
        """
        implemented = {'balance_sheet', 'cash_flow', 'income_statement'}
        if statement_type not in implemented:
            raise ValueError(f'enter valid statement type: {implemented}')
        directory = self._market_data_source.statement_dir
        filename = f"{self._market_data_source.file_prefix}_{ticker.replace('.TO', '_TO')}_{statement_type}.csv"

        if files_utils.check_file(directory=directory, file=filename):
            df = pd.read_csv(f"{directory}/{filename}").set_index("Breakdown")
            return df
        else:
            logger.logging.info(f'no {statement_type} data to read for {ticker}, now fetching new data from api')
            self.update_statement(ticker=ticker, statement_type=statement_type)
            return self.read_fundamentals(ticker=ticker, statement_type=statement_type)

    def read_dividends(self, ticker: str) -> pd.DataFrame:
        """
        Read dividends data saved locally in client data folder.
        If no .csv found, dividends data will be fetched

        :param ticker: Stock Ticker
        :return:
        """
        directory = self._market_data_source.statement_dir
        filename = f"{self._market_data_source.file_prefix}_{ticker}_dividends.csv"

        if files_utils.check_file(directory=directory, file=filename):
            df = pd.read_csv(f"{directory}/{filename}")
            df = df.set_index('date')
            df.index = pd.to_datetime(df.index)
            return df['dividend']
        else:
            logger.logging.info(f'no dividend data to read for {ticker}, now fetching new data from api')
            self.update_dividends(ticker=ticker)
            return self.read_dividends(ticker)

    def update_prices(self, ticker: str) -> None:
        self._market_data_source.get_prices(ticker=ticker)

    def update_fx(self, currency_pair: str) -> None:
        self._market_data_source.get_fx(currency_pair=currency_pair)

    def update_statement(self, ticker: str, statement_type: str) -> None:
        """
        Updates the statements data from the data source

        :param ticker: Stock ticker
        :param statement_type: 'balance_sheet', 'cash_flow', 'income_statement' or 'all'
        :return:
        """
        if statement_type == 'balance_sheet':
            self._statements_data_source.get_balance_sheet(ticker)
        elif statement_type == 'cash_flow':
            self._statements_data_source.get_cash_flow(ticker)
        elif statement_type == 'income_statement':
            self._statements_data_source.get_cash_flow(ticker)

        elif statement_type == 'all':
            self._statements_data_source.get_balance_sheet(ticker)
            self._statements_data_source.get_cash_flow(ticker)
            self._statements_data_source.get_income_statement(ticker)
        else:
            raise NotImplementedError({statement_type})

    def update_dividends(self, ticker: str) -> None:
        self._market_data_source.get_dividends(ticker=ticker)

    def get_splits(self, ticker: str) -> pd.DataFrame:
        """
        Read stock splits data saved locally in client data folder.
        If no .csv found, splits data will be fetched

        :param ticker:
        :return:
        """
        return self._market_data_source.get_splits(ticker=ticker)

    def last_data_point(self, ptf_currency: str = 'CAD') -> datetime:
        """
        Find last data point fetched in locally saved files.

        :param ptf_currency: portfolio currency
        :return:
        """
        last_data = self.read_fx(f'{ptf_currency}{ptf_currency}').sort_index().index[-1]
        return last_data
