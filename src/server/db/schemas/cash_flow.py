from sqlalchemy import Column, Integer, String, Float, Date
from sqlalchemy.orm import declarative_base

from src.server.core.entities.financials.cash_flows import CashFlow


Base = declarative_base()


class CashFlowDB(Base):
    __tablename__ = "cash_flows"

    id = Column(Integer, primary_key=True, index=True)
    event_date = Column(Date, nullable=False)
    flow_type = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    related_asset_id = Column(Integer, nullable=False)

    description = Column(String, default="")
    category = Column(String, default="")


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

class