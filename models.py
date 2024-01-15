from enum import Enum


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
