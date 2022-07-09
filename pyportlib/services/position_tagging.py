import json
from typing import List, Dict

from pyportlib.utils import files_utils, logger


class PositionTagging:
    _ACCOUNTS_DIRECTORY = files_utils.get_accounts_dir()
    _TAGGING_FILENAME = "position_tags.json"

    def __init__(self, account: str, tickers: List[str]):
        self._account = account
        self._tickers = tickers
        self._tags = dict()
        self.load()

    def __repr__(self):
        return f"{self._account} - Position Tags"

    def get(self, ticker: str) -> str:
        try:
            return self._tags[ticker]
        except KeyError:
            logger.logging.error(f"{ticker} is not in position tagging file, updating and trying again")
            self.load()
            return self._tags[ticker]

    def reset(self):
        self._create_default_tags()

    def load(self) -> None:
        if files_utils.check_file(f'{self._ACCOUNTS_DIRECTORY}{self._account}', self._TAGGING_FILENAME):
            with open(self._filename) as myfile:
                self._tags = json.loads(myfile.read())
            self._update()

        else:  # if file does not exist
            self._create_default_tags()

    @property
    def tags(self) -> Dict[str, str]:
        return self._tags

    @property
    def _filename(self) -> str:
        return f'{self._ACCOUNTS_DIRECTORY}{self._account}/{self._TAGGING_FILENAME}'

    def _default_tags(self) -> Dict[str, str]:
        return {k: "" for k in self._tickers}

    def _update(self) -> None:
        missing = set(self._tickers) - set(self._tags.keys())
        if len(missing):
            missing = {k: "" for k in missing}
            self._tags.update(missing)
            self._save()

    def _create_default_tags(self) -> None:
        self._tags = self._default_tags()
        self._save()

    def _save(self) -> None:
        with open(self._filename, 'w', encoding='utf-8') as f:
            json.dump(self._tags, f, ensure_ascii=False, indent=1)
        logger.logging.debug("position tags saved")
