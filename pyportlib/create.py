from pyportlib.containers.data_reader_container import DataReaderContainer
from pyportlib.portfolio import Portfolio
from pyportlib.position import Position
from pyportlib.utils import config_utils

conf = config_utils.data_config()
dr_container = DataReaderContainer(config=conf)


def portfolio(account: str, currency: str):
    ptf = Portfolio(account=account,
                    currency=currency,
                    datareader=dr_container.datareader())
    return ptf


def position(ticker: str, local_currency: str, tag: str = None):
    pos = Position(ticker=ticker,
                   local_currency=local_currency,
                   tag=tag,
                   datareader=dr_container.datareader)

    return pos
