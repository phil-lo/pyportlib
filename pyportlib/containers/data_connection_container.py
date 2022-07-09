from dependency_injector import containers, providers

from pyportlib.market_data_sources.yahoo_connection import YahooConnection


class DataConnectionContainer(containers.DeclarativeContainer):
    yahoo = providers.Singleton(YahooConnection)
