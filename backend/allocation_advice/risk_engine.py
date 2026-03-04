import pandas as pd
import numpy as np
from arch import arch_model
import yfinance as yf
from typing import Dict, Optional

class RiskEngine:
    """
    风险计算引擎，负责计算 VaR (Value at Risk) 和 GARCH 波动率预测。
    """
    
    def __init__(self, data_period="1y"):
        self.data_period = data_period

    def fetch_data(self, symbol: str) -> pd.Series:
        """
        获取资产的历史收盘价数据，并计算对数收益率。
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=self.data_period)
            if data.empty:
                return pd.Series()
            
            # 计算对数收益率
            data['Log_Return'] = np.log(data['Close'] / data['Close'].shift(1))
            return data['Log_Return'].dropna()
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return pd.Series()

    def calculate_var(self, returns: pd.Series, confidence_level=0.95) -> float:
        """
        计算历史模拟法 VaR (Value at Risk)。
        """
        if returns.empty:
            return 0.0
        # VaR 是分位数
        return np.percentile(returns, (1 - confidence_level) * 100)

    def fit_garch(self, returns: pd.Series):
        """
        拟合 GARCH(1,1) 模型并预测未来波动率。
        """
        if returns.empty or len(returns) < 30: # 数据太少无法拟合
            return None
        
        # 将收益率放大 100 倍以提高数值稳定性
        scaled_returns = returns * 100
        
        try:
            model = arch_model(scaled_returns, vol='Garch', p=1, q=1)
            res = model.fit(disp='off')
            return res
        except Exception as e:
            print(f"GARCH fitting failed: {e}")
            return None

    def analyze_asset_risk(self, symbol: str) -> Dict[str, str]:
        """
        分析单个资产的风险指标。
        """
        returns = self.fetch_data(symbol)
        if returns.empty:
            return {"error": f"无法获取 {symbol} 的历史数据"}

        # 1. 计算 VaR (95% 置信度)
        var_95 = self.calculate_var(returns, 0.95)
        
        # 2. GARCH 预测
        garch_res = self.fit_garch(returns)
        forecast_volatility = "N/A"
        if garch_res:
            forecast = garch_res.forecast(horizon=5)
            # 获取未来 5 天的年化波动率预测均值
            forecast_volatility = f"{np.mean(forecast.variance.iloc[-1].values)**0.5:.2f}% (5日预测)"

        return {
            "symbol": symbol,
            "VaR_95_daily": f"{var_95*100:.2f}%", # 转换为百分比
            "GARCH_volatility_forecast": forecast_volatility,
            "Interpretation": f"该资产在95%置信度下的单日最大潜在损失约为 {-var_95*100:.2f}%。"
        }
