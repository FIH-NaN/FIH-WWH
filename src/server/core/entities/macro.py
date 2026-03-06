
from dataclasses import dataclass, field


@dataclass(slots=True)
class MacroeconIndices:
    """
    Macroeconomic indices
    """
    risk_free: float

    # todo