from datetime import datetime
from typing import List, Union
import pandas as pd
from ..utils import df_utils, files_utils
from ..utils import logger


class CashAccount:
    NAME = "Cash Account"
    ACCOUNTS_DIRECTORY = files_utils.get_accounts_dir()
    CASH_INFO = ['Date', 'Direction', 'Amount']
    CASH_FILENAME = "cash.csv"

    def __init__(self, account):
        self.account = account
        self.directory = f"{self.ACCOUNTS_DIRECTORY}{self.account}"
        self._cash_changes = pd.DataFrame()
        self.load()

    def __repr__(self):
        return self.NAME

    def load(self):
        if files_utils.check_file(self.directory, self.CASH_FILENAME):
            cash = pd.read_csv(f"{self.directory}/{self.CASH_FILENAME}")
            try:
                cash.drop(columns='Unnamed: 0', inplace=True)
            except KeyError:
                pass
            finally:
                if df_utils.check_df_columns(df=cash, columns=self.CASH_INFO):
                    cash.set_index('Date', inplace=True)
                    cash.index.name = 'Date'
                    cash.index = pd.to_datetime(cash.index)
                    self._cash_changes = cash
                else:
                    logger.logging.info(f'cash file does not match requirements: {self.account}')
        else:
            # if new ptf, create required files to use it
            if not files_utils.check_dir(self.directory):
                files_utils.make_dir(self.directory)
            # create empty transaction file in new directory
            empty_cash = self._empty_cash()
            empty_cash.to_csv(f"{self.directory}/{self.CASH_FILENAME}")
            self._cash_changes = empty_cash

    @property
    def cash_changes(self):
        return self._cash_changes

    def get_cash_changes(self):
        return self.cash_changes

    def get_cash_change(self, date):
        c_ch = self.get_cash_changes()
        return c_ch.loc[self.get_cash_changes().index <= date, 'Amount'].sum()

    def _write(self, date: datetime, direction: str, amount: float):
        direction = direction.title()
        if direction not in ['Deposit', 'Withdrawal']:
            raise Exception(f'cash direction type not supported {direction}')

        self.cash_changes.loc[date, "Direction"] = direction
        self.cash_changes.loc[date, "Amount"] = amount

        self.cash_changes.to_csv(f"{self.directory}/{self.CASH_FILENAME}")
        self.load()

    def add(self, cash_changes: Union[List[dict], dict]):
        if cash_changes:
            if not hasattr(cash_changes, '__iter__'):
                cash_changes = [cash_changes]

            for cc in cash_changes:
                change = self._check(cc)
                self._write(date=change["Date"], direction=change['Direction'], amount=change['Amount'])

    def reset(self):
        empty_cash = self._empty_cash()
        empty_cash.to_csv(f"{self.directory}/{self.CASH_FILENAME}")
        self._cash_changes = empty_cash

    def _empty_cash(self):
        return pd.DataFrame(columns=self.CASH_INFO).set_index('Date')

    @staticmethod
    def _check(cash_change: dict):
        assert isinstance(cash_change.get("Date"), datetime)
        assert cash_change["Direction"] in ["Deposit", "Withdrawal"]
        assert isinstance(cash_change["Amount"], float)

        return cash_change
