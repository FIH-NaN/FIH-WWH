
from src.server.core.entities.card import Card


class BankAccount:
    pass


class DebitCard(Card):
    account: BankAccount
    pass

class CreditCard(Card):
    account: BankAccount
    pass

