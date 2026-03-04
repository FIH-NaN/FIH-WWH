from pydantic import BaseModel
from typing import Dict, List, Optional, Union

# 移除单独的 Transaction 类，直接使用字典或字符串
# class Transaction(BaseModel): ... 

class UserAssets(BaseModel):
    """
    表示用户的当前金融资产，支持多币种现金、股票、加密货币以及近期交易记录。
    """
    user_name: str
    cash_assets: Dict[str, float] # 货币代码 -> 数量 (例如: {"USD": 1000, "CNY": 5000, "EUR": 200})
    base_currency: str = "USD" # 计算总资产时的基准货币
    stocks: Dict[str, float] # 股票代码 -> 数量 (例如: {"AAPL": 10, "MSFT": 5})
    cryptos: Dict[str, float] # 符号 -> 数量 (例如: {"BTC": 0.5})
    risk_profile: str = "moderate" # 例如：conservative（保守）, moderate（稳健）, aggressive（激进）
    
    # 简化为字符串列表，用户可以直接输入自然语言描述的交易记录
    recent_transactions: List[str] = [] 

    def __str__(self):
        cash_str = ", ".join([f"{amount} {currency}" for currency, amount in self.cash_assets.items()])
        stocks_str = ", ".join([f"{amount} shares of {symbol}" for symbol, amount in self.stocks.items()])
        transactions_str = "\n  ".join(self.recent_transactions) if self.recent_transactions else "无近期交易"
        
        return (f"用户名: {self.user_name}\n"
                f"现金资产: {cash_str}\n"
                f"基准货币: {self.base_currency}\n"
                f"股票持仓: {stocks_str}\n"
                f"加密货币: {self.cryptos}\n"
                f"风险偏好: {self.risk_profile}\n"
                f"近期交易记录:\n  {transactions_str}")
