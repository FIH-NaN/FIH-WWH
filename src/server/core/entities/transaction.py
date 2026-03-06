from enum import Enum


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


class Transaction:
    # todo
    pass