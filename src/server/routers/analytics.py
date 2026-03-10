from datetime import date
import json
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
import requests
from sqlalchemy.orm import Session

from src.server.config import get_settings
from src.server.db.database import get_db
from src.server.db.tables.advisor_chat import AdvisorConversation, AdvisorMessage
from src.server.db.tables.budget import BudgetItem
from src.server.db.tables.user import User
from src.server.routers.web_view_model.schemas import SuccessResponse
from src.server.services.auth.security import get_current_user
from src.server.services.financial_analysis.dashboard_metrics import DashboardMetricsService
from src.server.services.financial_analysis.wellness_metrics import WellnessMetricsService
from src.server.services.user_data.asset_data import UserAssetDataManager


class BudgetUpsertItem(BaseModel):
    flow_type: str
    category: str
    amount: float


class BudgetUpsertPayload(BaseModel):
    month_key: Optional[str] = None
    items: List[BudgetUpsertItem] = Field(default_factory=list)


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None


router = APIRouter(tags=["analytics"])


def _extract_chat_text(body: dict) -> str:
    text = WellnessMetricsService._extract_minimax_text(body)
    if text:
        return text
    if isinstance(body.get("error"), str):
        return str(body.get("error"))
    return ""


def _minimax_chat_reply(user_id: int, history: List[dict], db: Session) -> str:
    settings = get_settings()
    api_key = (settings.MINIMAX_API_KEY or "").strip()
    if not api_key:
        return "MINIMAX_API_KEY is not configured."

    overview = UserAssetDataManager.get_wealth_overview(db=db, user_id=user_id)
    totals = DashboardMetricsService.build_totals(db=db, user_id=user_id)

    system_prompt = (
        "You are a personal finance assistant for Wealth Wellness Hub. "
        "Give concise and practical advice in plain English. "
        "Use the provided portfolio context and conversation history. "
        "Do not use markdown tables."
    )

    context_prompt = (
        f"Portfolio score: {overview.get('overall_score', 0)}. "
        f"Total income: {totals.get('total_income', 0):.2f}. "
        f"Total expense: {totals.get('total_expense', 0):.2f}. "
        f"Savings rate: {totals.get('savings_rate', 0):.2f}%."
    )

    messages = [{"role": "user", "content": [{"type": "text", "text": f"Context: {context_prompt}"}]}]
    for item in history[-12:]:
        role = str(item.get("role") or "user")
        content = str(item.get("content") or "").strip()
        if not content:
            continue
        messages.append({"role": role, "content": [{"type": "text", "text": content}]})

    payload = {
        "model": (settings.MINIMAX_MODEL or "MiniMax-M2.5").strip(),
        "system": system_prompt,
        "messages": messages,
        "temperature": 0.5,
        "max_tokens": 900,
    }

    try:
        resp = requests.post(
            (settings.MINIMAX_API_URL or "https://api.minimaxi.com/anthropic/v1/messages").strip(),
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=60,
        )
        if resp.status_code != 200:
            try:
                err = resp.json()
                return f"MiniMax error {resp.status_code}: {err}"
            except Exception:
                return f"MiniMax error {resp.status_code}: {resp.text[:180]}"
        body = resp.json()
        if not isinstance(body, dict):
            return "MiniMax returned an invalid response."
        reply = _extract_chat_text(body).strip()
        return reply or "MiniMax returned empty response."
    except Exception as exc:
        return f"MiniMax request failed: {str(exc)}"


@router.get("/dashboard/balance-sheet", response_model=SuccessResponse)
def dashboard_balance_sheet(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    payload = DashboardMetricsService.build_balance_sheet(db=db, user_id=int(getattr(user, "id")))
    return SuccessResponse(success=True, data=payload)


@router.get("/dashboard/totals", response_model=SuccessResponse)
def dashboard_totals(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    payload = DashboardMetricsService.build_totals(db=db, user_id=int(getattr(user, "id")))
    return SuccessResponse(success=True, data=payload)


@router.get("/dashboard/income-statement", response_model=SuccessResponse)
def dashboard_income_statement(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    payload = DashboardMetricsService.build_income_statement(db=db, user_id=int(getattr(user, "id")))
    return SuccessResponse(success=True, data=payload)


@router.get("/dashboard/summary", response_model=SuccessResponse)
def dashboard_summary(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = int(getattr(user, "id"))
    balance_sheet = DashboardMetricsService.build_balance_sheet(db=db, user_id=user_id)
    totals = DashboardMetricsService.build_totals(db=db, user_id=user_id)
    income_statement = DashboardMetricsService.build_income_statement(db=db, user_id=user_id)
    return SuccessResponse(
        success=True,
        data={
            "net_worth": balance_sheet["net_worth"],
            "total_income": totals["total_income"],
            "total_expense": totals["total_expense"],
            "savings_rate": totals["savings_rate"],
            "balance_sheet": balance_sheet,
            "income_statement": income_statement,
        },
    )


@router.get("/accounting/current-month", response_model=SuccessResponse)
def accounting_current_month(
    flow: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    flow_key = flow.strip().lower()
    if flow_key not in {"income", "expense"}:
        raise HTTPException(status_code=400, detail="flow must be income or expense")
    payload = DashboardMetricsService.build_accounting_current_month(db=db, user_id=int(getattr(user, "id")), flow=flow_key)
    return SuccessResponse(success=True, data=payload)


@router.get("/accounting/series-12m", response_model=SuccessResponse)
def accounting_series_12m(
    flow: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    flow_key = flow.strip().lower()
    if flow_key not in {"income", "expense"}:
        raise HTTPException(status_code=400, detail="flow must be income or expense")
    payload = DashboardMetricsService.build_accounting_series_12m(db=db, user_id=int(getattr(user, "id")), flow=flow_key)
    return SuccessResponse(success=True, data=payload)


@router.get("/portfolio/summary", response_model=SuccessResponse)
def portfolio_summary(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    payload = DashboardMetricsService.build_portfolio_summary(db=db, user_id=int(getattr(user, "id")))
    return SuccessResponse(success=True, data=payload)


@router.get("/portfolio/investment-holdings", response_model=SuccessResponse)
def portfolio_investment_holdings(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    payload = DashboardMetricsService.build_investment_holdings_distribution(db=db, user_id=int(getattr(user, "id")))
    return SuccessResponse(success=True, data=payload)


@router.get("/market/indicators", response_model=SuccessResponse)
def market_indicators(user: User = Depends(get_current_user)):
    del user
    payload = DashboardMetricsService.build_market_indicators()
    return SuccessResponse(success=True, data=payload)


@router.get("/dashboard/budgets", response_model=SuccessResponse)
def get_budgets(
    month_key: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    target_month = month_key or date.today().strftime("%Y-%m")
    rows = db.query(BudgetItem).filter(BudgetItem.user_id == int(getattr(user, "id")), BudgetItem.month_key == target_month).all()
    items = [
        {
            "id": int(getattr(row, "id")),
            "flow_type": str(getattr(row, "flow_type")),
            "category": str(getattr(row, "category")),
            "amount": float(getattr(row, "amount") or 0.0),
        }
        for row in rows
    ]
    return SuccessResponse(success=True, data={"month_key": target_month, "items": items})


@router.put("/dashboard/budgets", response_model=SuccessResponse)
def upsert_budgets(
    payload: BudgetUpsertPayload,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    target_month = payload.month_key or date.today().strftime("%Y-%m")
    user_id = int(getattr(user, "id"))

    for item in payload.items:
        flow = item.flow_type.strip().lower()
        if flow not in {"income", "expense"}:
            raise HTTPException(status_code=400, detail="flow_type must be income or expense")

        category = item.category.strip() or "Uncategorized"
        row = db.query(BudgetItem).filter(
            BudgetItem.user_id == user_id,
            BudgetItem.month_key == target_month,
            BudgetItem.flow_type == flow,
            BudgetItem.category == category,
        ).first()

        if row is None:
            row = BudgetItem(user_id=user_id, month_key=target_month, flow_type=flow, category=category)
            db.add(row)

        setattr(row, "amount", float(item.amount or 0.0))

    db.commit()
    return get_budgets(month_key=target_month, user=user, db=db)


@router.get("/advisor/chat/conversations", response_model=SuccessResponse)
def list_conversations(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = (
        db.query(AdvisorConversation)
        .filter(AdvisorConversation.user_id == int(getattr(user, "id")))
        .order_by(AdvisorConversation.updated_at.desc())
        .all()
    )
    items = [
        {
            "id": int(getattr(row, "id")),
            "title": str(getattr(row, "title") or "New conversation"),
            "updated_at": getattr(row, "updated_at"),
        }
        for row in rows
    ]
    return SuccessResponse(success=True, data={"items": items})


@router.get("/advisor/chat/conversations/{conversation_id}", response_model=SuccessResponse)
def get_conversation(conversation_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conversation = db.query(AdvisorConversation).filter(
        AdvisorConversation.id == conversation_id,
        AdvisorConversation.user_id == int(getattr(user, "id")),
    ).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = db.query(AdvisorMessage).filter(
        AdvisorMessage.conversation_id == conversation_id,
        AdvisorMessage.user_id == int(getattr(user, "id")),
    ).order_by(AdvisorMessage.created_at.asc()).all()

    payload = {
        "id": int(getattr(conversation, "id")),
        "title": str(getattr(conversation, "title") or "New conversation"),
        "messages": [
            {
                "id": int(getattr(row, "id")),
                "role": str(getattr(row, "role")),
                "content": str(getattr(row, "content")),
                "created_at": getattr(row, "created_at"),
            }
            for row in messages
        ],
    }
    return SuccessResponse(success=True, data=payload)


@router.post("/advisor/chat/messages", response_model=SuccessResponse)
def send_message(payload: ChatRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = int(getattr(user, "id"))
    message = payload.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="message is required")

    conversation = None
    if payload.conversation_id is not None:
        conversation = db.query(AdvisorConversation).filter(
            AdvisorConversation.id == payload.conversation_id,
            AdvisorConversation.user_id == user_id,
        ).first()
    if conversation is None:
        conversation = AdvisorConversation(user_id=user_id, title=(message[:48] or "New conversation"))
        db.add(conversation)
        db.flush()

    user_row = AdvisorMessage(conversation_id=conversation.id, user_id=user_id, role="user", content=message)
    db.add(user_row)

    prior_rows = db.query(AdvisorMessage).filter(
        AdvisorMessage.conversation_id == int(getattr(conversation, "id")),
        AdvisorMessage.user_id == user_id,
    ).order_by(AdvisorMessage.created_at.asc()).all()
    history = [
        {
            "role": str(getattr(row, "role") or "user"),
            "content": str(getattr(row, "content") or ""),
        }
        for row in prior_rows
    ]
    history.append({"role": "user", "content": message})

    assistant_text = _minimax_chat_reply(user_id=user_id, history=history, db=db)
    assistant_row = AdvisorMessage(conversation_id=conversation.id, user_id=user_id, role="assistant", content=assistant_text)
    db.add(assistant_row)

    db.commit()
    return get_conversation(conversation_id=int(getattr(conversation, "id")), user=user, db=db)
