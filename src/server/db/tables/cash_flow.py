from datetime import date
from sqlalchemy import Column, Integer, String, Float, Date
from sqlalchemy.orm import Mapped, mapped_column

from src.server.core.entities.currency import Currency
from src.server.core.entities.cash_flows import CashFlow, CashFlowType
from src.server.db.database import Base


class CashFlowDB(Base):
    __tablename__ = "cash_flows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_date: Mapped[date] = mapped_column(Date, nullable=False)
    flow_type: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String, nullable=False)
    related_asset_id: Mapped[int] = mapped_column(Integer, nullable=False)

    description: Mapped[str] = mapped_column(String, default="")
    category: Mapped[str] = mapped_column(String, default="")


def to_dataclass(db_obj: CashFlowDB) -> CashFlow:
    return CashFlow(
        id=db_obj.id,
        event_date=db_obj.event_date,
        flow_type=CashFlowType(db_obj.flow_type),
        amount=db_obj.amount,
        currency=Currency(db_obj.currency),
        related_asset_id=db_obj.related_asset_id,
        description=db_obj.description,
        category=db_obj.category,
    )

