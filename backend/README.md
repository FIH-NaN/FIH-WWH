# 全球智能投资顾问 (Global Investment Advisor) - 使用指南

这是一个基于多 Agent 架构的智能投资顾问系统。它通过分析用户的多币种资产、股票、加密货币持仓以及近期交易行为，结合实时市场数据和风险模型（GARCH/VaR），提供个性化的投资组合改善建议。

## 🚀 快速开始

### 1. 环境准备

确保已安装 Python 3.9+。建议在虚拟环境中安装依赖：

```bash
# 安装核心依赖
pip install -r requirements.txt
```

### 2. 配置 API Key

在项目根目录下创建一个 `.env` 文件（可参考 `.env.example`）：

```text
OPENAI_API_KEY=your_openai_api_key_here
```

## 📖 如何使用功能

你可以通过导入 `get_investment_advice` 函数来获取投资建议。该函数接收一个 `UserAssets` 对象作为输入。

### 核心调用示例

```python
from allocation_advice.multi_agent import get_investment_advice
from allocation_advice.models import UserAssets

# 1. 构建用户资产数据模型
user_assets = UserAssets(
    user_name="张三 (Zhang San)",
    # 多币种现金持仓
    cash_assets={
        "CNY": 500000.0,  # 50万人民币
        "USD": 10000.0,   # 1万美元
    },
    base_currency="CNY",  # 计算总资产时的基准货币
    # 股票持仓 (支持美股、港股、A股代码)
    stocks={
        "AAPL": 50,       # 苹果 (美股)
        "0700.HK": 200,   # 腾讯 (港股)
        "600519.SS": 100  # 贵州茅台 (A股)
    },
    # 加密货币持仓
    cryptos={
        "BTC": 0.5,
        "ETH": 5.0
    },
    risk_profile="moderate",  # 风险偏好: conservative/moderate/aggressive
    # 近期交易记录 (支持自然语言描述，用于行为分析)
    recent_transactions=[
        "2024-03-01 买入 BTC 0.1个 单价62000 USD",
        "2024-03-05 买入 BTC 0.1个 单价68000 USD (追涨)",
        "2024-02-15 卖出 AAPL 10股 单价180 USD"
    ]
)

# 2. 获取 AI 投资顾问建议
# 该过程会触发多 Agent 协作：
# - Researcher: 查询实时汇率、股价、市场新闻并计算 GARCH/VaR 风险指标
# - Advisor: 综合所有信息生成包含资产配比、行为诊断和风险提示的报告
advice = get_investment_advice(user_assets)

# 3. 输出建议报告
print(advice)
```

## �️ 核心模块说明

- **`UserAssets`**: 定义用户资产的统一数据结构，支持多币种和交易历史。
- **`get_investment_advice`**: 一键式接口，启动多 Agent 工作流并返回 Markdown 格式的建议报告。
- **风险引擎**: 内部集成 GARCH(1,1) 模型和历史模拟法 VaR，自动评估用户投资组合的波动风险。

## ⚠️ 注意事项

1. **网络连接**: 实时数据获取依赖 `yfinance` 和 `duckduckgo-search`，请确保网络环境能够访问相关服务。
2. **API 消耗**: 建议生成过程涉及多次 LLM 调用，请确保 API 额度充足。
3. **免责声明**: 本工具生成的建议仅供参考，不构成任何法律意义上的投资建议。
