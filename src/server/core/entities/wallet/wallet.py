from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from src.server.core.entities.wallet.card import BankCard, CryptoCard
from src.server.core.entities.wallet.bank import DebitCard, CreditCard
from src.server.core.entities.wallet.crypto import CryptoCard


@dataclass(slots=True)
class WealthWallet:
		id: int
		bank_cards: Dict[int, BankCard]
		crypto_cards: Dict[int, CryptoCard]

		# todo

