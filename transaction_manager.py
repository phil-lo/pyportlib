from data_sources.data_source_manager import DataSourceManager
from transaction import Transaction
from utils.df_utils import check_csv
from utils.files_utils import check_file, check_dir, make_dir
import pandas as pd


class TransactionManager(object):
    name = "Transactions Manager"
    ACCOUNTS_DIRECTORY = "client_data/accounts/"

    def __init__(self, account, connection: DataSourceManager):
        self.account = account
        self.directory = f"{self.ACCOUNTS_DIRECTORY}{self.account}"
        self.filename = f"{self.account}_transactions.csv"
        self.transactions = self.fetch()
        self.connection = connection

    def __repr__(self):
        return self.name

    def fetch(self) -> pd.DataFrame:
        if check_file(self.directory, self.filename):
            trx = pd.read_csv(f"{self.directory}/{self.filename}")
            try:
                trx.drop(columns='Unnamed: 0', inplace=True)
            except KeyError:
                pass
            finally:
                if check_csv(trx, Transaction.TRANSACTIONS_INFO):
                    trx.set_index('Date', inplace=True)
                    trx.index.name = 'Date'
                    return trx
                else:
                    raise KeyError("transactions csv file has wrong format")
        else:
            # transactions do not exist check if portfolio directory exists
            if not check_dir(self.directory):
                make_dir(self.directory)
            # create empty transaction file
            empty_transactions = pd.DataFrame(columns=Transaction.TRANSACTIONS_INFO).set_index('Date')
            empty_transactions.to_csv(f"{self.directory}/{self.filename}")
            return empty_transactions

    def write(self) -> None:
        self.transactions.index.name = 'Date'
        self.transactions.to_csv(f"{self.directory}/{self.filename}")
        print('transactions file updated')

    def add(self, transaction: Transaction) -> None:
        new = transaction.get()
        self.transactions = pd.concat([self.transactions, new])

        new_qty = self.transactions.Quantity.loc[self.transactions.Ticker == transaction.ticker].sum()
        excess = -1 * (transaction.quantity - (transaction.quantity - new_qty))
        if new_qty < 0:
            raise ValueError(f'no short positions allowed, you sold {excess} units too many')

        self.write()
        print(f'{transaction} added to account: {self.account}')

    def all_tickers(self) -> list:
        try:
            tickers = list(set(self.transactions.Ticker))
        except AttributeError:
            return []
        return tickers

    def live_tickers(self) -> list:
        live_tickers = self.transactions.groupby('Ticker').sum()
        try:
            live_tickers = live_tickers.loc[live_tickers.Quantity > 0]
        except AttributeError:
            return []
        return list(live_tickers.index)

    def total_fees(self) -> float:
        return self.transactions.Fees.sum()
    
    def first_trx_date(self):
        return self.transactions.idxmin()

    # FIXME compute cad when trx are fetched
    def compute_wac(self):
        tickers = self.live_tickers()
        buys = self.transactions.loc[(self.transactions.Ticker.isin(tickers)) & (self.transactions.Type == 'Buy')]
        fx = self.connection.fx(read=True, currency='USD')
        fx = fx.loc[fx.index.isin(buys.index)]['Close']
        for date in set(buys.index):
            buys.loc[(buys.Currency == 'USD') & (buys.index == date), 'PriceCad'] = buys.loc[(buys.Currency == 'USD') & (buys.index == date), 'Price'] * fx.loc[date]
        buys.loc[buys.Currency == 'CAD', 'PriceCad'] = buys.loc[buys.Currency == 'CAD', 'Price']
        print('')