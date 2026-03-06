
from src.server.core.entities.card import Card


class CryptoAccount:
    pass


class CryptoCard(Card):
    account: CryptoAccount
    pass