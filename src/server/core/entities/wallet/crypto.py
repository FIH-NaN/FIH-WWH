
from src.server.core.entities.wallet.card import Card


class CryptoAccount:
    pass


class CryptoCard(Card):
    account: CryptoAccount
    pass