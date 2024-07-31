from enum import Enum
import json
from environs import Env
from streamlit import session_state
from typing import Any


class Col(Enum):
    TransactionDate = "Transaction Date"
    Amount = "Amount"
    TransactionType = "Transaction Type"
    AccountType = "Account"
    Description = "Description"
    Label = "Label"


class Label(Enum):
    IncomeMichael = "Michael's Income"
    IncomeStephanie = "Stephanie's Income"
    ExpenseMortgage = "Mortgage Payment"
    ExpenseNeeds = "Need's Payment"
    ExpenseWants = "Want's Payment"


class EnvironmentReader():
    env: Env
    DATA_FILE_PATH: str
    CURRENT_YYYY: int
    MAX_MONTH: int

    def __init__(self) -> None:
        self.env = Env()
        self.env.read_env()
        self.DATA_FILE_PATH = self.env.str(
            'DATA_FILE_PATH', validate=lambda val: len(val) > 1)
        self.CURRENT_YYYY = self.env.int(
            'CURRENT_YYYY', validate=lambda val: val > 2010 and val < 2050)
        self.MAX_MONTH = self.env.int(
            'MAX_MONTH', validate=lambda val: val >= 1 and val <= 12)


class SessionStore():
    state: Any

    def __init__(self, session_state) -> None:
        if "count" not in session_state:
            session_state.count = 0

        if "amount_sum" not in session_state:
            session_state.amount_sum = 0.0

        self.state = session_state


def main() -> None:
    test_env = EnvironmentReader()


if __name__ == "__main__":
    main()
