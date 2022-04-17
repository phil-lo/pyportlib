from datetime import datetime

from ..utils import logger


class CashChange:
    _NAME = "CashChange"
    _DIRECTIONS = ["Deposit", "Withdrawal"]
    _INFO = ['Date', 'Direction', 'Amount']

    def __init__(self, date: datetime, direction: str, amount: float):
        self.date = date
        self.direction = direction
        self.amount = amount
        self._check()

    def __repr__(self):
        return f"{self._NAME} - {self.date.date()} - {self.direction} - {self.amount}"

    @property
    def info(self):
        return {"Date": self.date,
                "Direction": self.direction,
                "Amount": self.amount}

    def _check(self):
        assert isinstance(self.info.get("Date"), datetime)
        assert self.info["Direction"] in self._DIRECTIONS
        assert isinstance(self.info["Amount"], float)
        if (self.direction == "Deposit" and self.amount < 0) or \
                (self.direction == "Withdrawals" and self.amount > 0):
            logger.logging.error(f"{self.direction} and {self.amount} don't match")