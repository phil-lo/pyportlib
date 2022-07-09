import json
from typing import List

from pyportlib.utils import files_utils


def make_config_dir(directory: str) -> None:
    """
    Create the config directory
    :param directory: location
    :return:
    """
    if not files_utils.check_dir(directory):
        files_utils.make_dir(directory)


def fetch_tickers_to_ignore() -> List[str]:
    """
    Tickers to ignore during transactions import from questrade. This is useful when importing a prior transaction
    history and a certain corp actions makes the data not available and it is simpler to ignore the transactions
    linked to the company. Should not be used by user.
    :return:
    """
    with open(f'{files_utils.get_config_dir()}config.json') as myfile:
        data = json.loads(myfile.read())
    tickers = data.get('ticker_ignore', None)

    if not tickers:
        return []
    return list(tickers.values())


def data_config() -> dict:
    """
    Fetch the datasources specified in the config file. Should not be used by user.
    :return:
    """
    with open(f'{files_utils.get_config_dir()}config.json') as myfile:
        data = json.loads(myfile.read())
    source = data['datasource']

    return source


def create_default_config(directory: str) -> None:
    """
    Create a default config .json file when first importing pyportlib. Should not be used by user.
    :param directory: string specifying the full path of the directory
    :return:
    """
    name = 'config.json'
    if not files_utils.check_file(directory, name):
        default_config = {
            "datasource": {
                "statements": "yahoo",
                "market_data": "yahoo"
            },
            "ticker_ignore": {
                "1": ""
            }
        }
        with open(f'{directory}/{name}', 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=1)
