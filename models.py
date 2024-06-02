from enum import Enum
from environs import Env


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


def main() -> None:
    test_env = EnvironmentReader()


if __name__ == "__main__":
    main()
