from dependency_injector import containers, providers

from pyportlib.containers.data_connection_container import DataConnectionContainer
from pyportlib.services.data_reader import DataReader


class DataReaderContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    connection_container = providers.Container(DataConnectionContainer)

    market_data_source = providers.Selector(
        config.market_data,
        yahoo=connection_container.yahoo
    )

    statements_data_source = providers.Selector(
        config.statements,
        yahoo=connection_container.yahoo
    )

    datareader = providers.Singleton(DataReader,
                                     market_data_source=market_data_source,
                                     statements_data_source=statements_data_source)
