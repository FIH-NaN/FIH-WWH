import yfinance as yf
from langchain_core.tools import tool
from typing import Optional, List
from duckduckgo_search import DDGS
from .risk_engine import RiskEngine

risk_engine = RiskEngine()

@tool
def get_exchange_rate(currency_pair: str) -> str:
    """
    获取指定货币对的当前汇率。
    实现原理：使用 yfinance 库查询 Yahoo Finance 上的汇率代码（如 "USDCNY=X"），获取最新的收盘价作为汇率。
    Args:
        currency_pair: 要查询的货币对，例如 "USDCNY=X" 表示美元兑人民币，"EURUSD=X" 表示欧元兑美元。
    Returns:
        当前汇率的字符串表示。
    """
    try:
        ticker = yf.Ticker(currency_pair)
        data = ticker.history(period="1d")
        if data.empty:
            return f"无法找到 {currency_pair} 的汇率。"
        rate = data['Close'].iloc[-1]
        return f"{currency_pair} 的当前汇率是 {rate:.4f}。"
    except Exception as e:
        return f"获取 {currency_pair} 汇率时出错: {str(e)}"

@tool
def get_stock_price(symbol: str) -> str:
    """
    获取指定股票的当前价格。
    实现原理：使用 yfinance 库根据股票代码（如 "AAPL", "MSFT"）查询最近一天的交易数据，并提取最新的收盘价。
    Args:
        symbol: 股票代码，例如 "AAPL" (苹果), "MSFT" (微软), "000001.SS" (上证指数)。
    Returns:
        当前股票价格的字符串表示。
    """
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d")
        if data.empty:
            return f"无法找到股票 {symbol} 的数据。"
        price = data['Close'].iloc[-1]
        info = ticker.info
        name = info.get('longName', symbol)
        return f"{name} ({symbol}) 的当前价格是 {price:.2f}。"
    except Exception as e:
        return f"获取股票 {symbol} 价格时出错: {str(e)}"

@tool
def get_crypto_price(symbol: str) -> str:
    """
    获取加密货币的当前价格。
    实现原理：使用 yfinance 库查询 Yahoo Finance 上的加密货币代码（通常以 "-USD" 结尾），获取最新价格。
    Args:
        symbol: 加密货币代码，例如 "BTC-USD", "ETH-USD"。
    Returns:
        当前加密货币价格的字符串表示。
    """
    try:
        # yfinance 使用类似 BTC-USD 的代码格式
        if not symbol.endswith("-USD") and "-" not in symbol:
            symbol = f"{symbol}-USD"
            
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d")
        if data.empty:
            return f"无法找到 {symbol} 的加密货币数据。"
        price = data['Close'].iloc[-1]
        return f"{symbol} 的当前价格是 {price:.2f}。"
    except Exception as e:
        return f"获取 {symbol} 加密货币价格时出错: {str(e)}"

@tool
def get_market_news(query: str) -> str:
    """
    获取与查询相关的近期市场新闻。
    实现原理：目前为模拟实现，返回固定的模拟新闻数据。在生产环境中应替换为 NewsAPI 或类似的实时新闻服务。
    Args:
        query: 要搜索新闻的主题，例如 "美国股市", "比特币", "黄金"。
    Returns:
        近期新闻标题的摘要。
    """
    # 这是一个模拟实现，因为真实的新闻 API 通常需要密钥
    # 在真实场景中，请使用 Google Search API 或 News API
    return f"关于 {query} 的模拟新闻: 市场波动较大。专家建议分散投资。近期报告显示科技板块趋势向好。"

@tool
def search_web(query: str) -> str:
    """
    搜索网络以获取国际局势、新法规或一般信息。
    实现原理：使用 duckduckgo-search 库调用 DuckDuckGo 搜索引擎，无需 API Key 即可获取最新的网页搜索结果摘要。
    Args:
        query: 搜索查询词，例如 "美国最新加密货币法规", "2025全球经济展望"。
    Returns:
        搜索结果的摘要。
    """
    try:
        results = DDGS().text(query, max_results=3)
        if not results:
            return "未找到搜索结果。"
        
        formatted_results = []
        for r in results:
            formatted_results.append(f"- {r['title']}: {r['body']}")
            
        return "\n".join(formatted_results)
    except Exception as e:
        return f"搜索网络时出错: {str(e)}"

@tool
def calculate_portfolio_risk(symbols: str) -> str:
    """
    计算指定资产列表的风险指标（VaR 和 GARCH 波动率预测）。
    
    Args:
        symbols: 逗号分隔的资产代码字符串，例如 "AAPL,BTC-USD,600519.SS"。
        
    Returns:
        包含每个资产风险分析结果的文本报告。
    """
    symbol_list = [s.strip() for s in symbols.split(',')]
    report = ["### 定量风险分析报告 (Quantitative Risk Analysis)"]
    
    for symbol in symbol_list:
        try:
            # 简单处理：如果是加密货币且没后缀，加上 -USD
            search_symbol = symbol
            if symbol.upper() in ["BTC", "ETH", "SOL", "DOGE"] and "-" not in symbol:
                search_symbol = f"{symbol}-USD"
                
            result = risk_engine.analyze_asset_risk(search_symbol)
            
            if "error" in result:
                report.append(f"- **{symbol}**: 数据获取失败 ({result['error']})")
            else:
                report.append(f"- **{symbol}**:")
                report.append(f"  - 日度 VaR (95%): {result['VaR_95_daily']}")
                report.append(f"  - GARCH 波动率预测: {result['GARCH_volatility_forecast']}")
                report.append(f"  - 解读: {result['Interpretation']}")
                
        except Exception as e:
            report.append(f"- **{symbol}**: 分析出错 ({str(e)})")
            
    return "\n".join(report)
