
from src.server.core.entities.wallet.card import Card


class BankAccount:
    pass


class DebitCard(Card):
    account: BankAccount
    pass

class CreditCard(Card):
    account: BankAccount
    pass

