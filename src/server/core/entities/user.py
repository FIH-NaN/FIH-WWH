
from dataclasses import dataclass, field

@dataclass(slots=True)
class User:

    id: int
    user_name: str
    password_hash: str
    account_number: str

    pass