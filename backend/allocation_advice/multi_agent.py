from typing import Annotated, Sequence, TypedDict, Union, List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, FunctionMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import operator
from .tools import get_exchange_rate, get_stock_price, get_crypto_price, get_market_news, search_web, calculate_portfolio_risk
from .models import UserAssets
import os

# 定义状态
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    user_assets: str

# 工具列表 - 重新添加了股票价格工具
tools = [get_exchange_rate, get_stock_price, get_crypto_price, get_market_news, search_web, calculate_portfolio_risk]

def get_llm():
    if not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY not found in environment variables.")
    return ChatOpenAI(model="gpt-3.5-turbo", temperature=0.05)

# --- 节点 ---

def researcher_agent(state: AgentState):
    """
    负责收集市场数据、国际局势和法规信息的 Agent。
    """
    messages = state["messages"]
    user_assets = state["user_assets"]
    llm = get_llm()
    
    # 定义研究员的角色和任务
    system_message = (
        "你是一名全球市场研究员。你的目标是为用户的投资组合和宏观环境收集全面的数据。\n"
        f"用户投资组合详情: {user_assets}\n"
        "你的任务:\n"
        "1. 识别投资组合中的所有资产（**包括多种法定货币现金、股票**和加密货币）。\n"
        "2. 识别用户的**近期交易记录**，分析其交易行为模式（如是否存在频繁交易、追涨杀跌等）。\n"
        "3. 使用可用工具获取每项资产的当前价格/汇率。\n"
        "   - **注意**：对于用户持有的每一种非基准货币，查询其对基准货币的汇率。\n"
        "   - **注意**：对于用户持有的股票，查询其当前股价。\n"
        "4. **风险分析**: 使用 'calculate_portfolio_risk' 工具对主要资产（股票、加密货币）进行定量风险分析（VaR 和 GARCH 波动率预测）。\n"
        "5. 关键: 使用 'search_web' 工具调查:\n"
        "   - 当前影响主要货币和股市的国际地缘政治局势。\n"
        "   - 新的金融法规（特别是关于加密货币/跨境金融的）。\n"
        "   - **市场热点与板块趋势**: 搜索当前市场上最热门的板块以及跌幅较大的板块。\n"
        "6. 清晰地总结所有收集到的数据（价格 + 宏观背景 + 市场热点 + **交易行为分析** + **风险分析报告**）。暂时不要给出建议。"
    )
    
    # 我们将工具绑定到 LLM
    llm_with_tools = llm.bind_tools(tools)
    
    # 预置系统消息
    response = llm_with_tools.invoke([SystemMessage(content=system_message)] + list(messages))
    
    return {"messages": [response]}

def advisor_agent(state: AgentState):
    """
    负责根据研究结果给出建议的 Agent。
    """
    messages = state["messages"]
    user_assets = state["user_assets"]
    llm = get_llm()
    
    system_message = (
        "你是一名高级财富管理顾问。你正在审阅全球市场研究员的调查结果。\n"
        f"用户投资组合详情: {user_assets}\n"
        "你的任务:\n"
        "1. 审阅研究员提供的市场数据（汇率、股价、币价）、地缘政治局势、新法规、市场热点板块以及**用户交易行为分析**。\n"
        "2. 计算投资组合的当前总价值（将所有外币、股票和加密货币换算为基准货币）。\n"
        "3. 提供一份‘投资组合改善计划’，包含:\n"
        "   - **多币种配置分析**: 评估持有不同法币的风险与机会。\n"
        "   - **股票与板块趋势分析**: 评估股票持仓，结合市场热点给出调整建议。\n"
        "   - **定量风险提示** (CRITICAL): \n"
        "       - 必须逐一列出主要资产的风险数据。\n"
        "       - 格式要求: '资产名: 日度VaR [数值], GARCH波动率 [数值] -> [简短评价]'\n"
        "       - 例如: 'BTC: 日度VaR -3.72%, GARCH波动率 2.84% -> 短期波动剧烈，需注意回撤风险。'\n"
        "       - 禁止只给出笼统的定性描述（如'风险较高'），必须包含数字。\n"
        "   - **交易行为诊断**: \n"
        "       - 基于用户的近期交易记录，点评其操作习惯（例如：‘您近期在比特币高点频繁买入，存在追涨风险’）。\n"
        "       - 给出改善交易习惯的建议（例如：‘建议采用定投策略，减少单笔大额择时操作’）。\n"
        "   - 资产配置分析: 考虑到风险，目前的分配是否健康？\n"
        "   - 监管影响: 新法律如何影响用户的具体持仓？\n"
        "   - 地缘政治策略: 如何对冲当前的全球不稳定性。\n"
        "   - 可执行的建议: 改善投资组合的具体步骤。\n"
        "请保持专业、战略性，并针对用户的姓名和个人情况进行个性化定制。"
    )
    
    response = llm.invoke([SystemMessage(content=system_message)] + list(messages))
    
    return {"messages": [response]}

def should_continue(state: AgentState):
    """
    确定研究员是否需要使用工具。
    """
    messages = state["messages"]
    last_message = messages[-1]
    
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"
    return "advisor"

# --- 图构建 ---

def create_multi_agent_graph():
    workflow = StateGraph(AgentState)
    
    # 添加节点
    workflow.add_node("researcher", researcher_agent)
    workflow.add_node("tools", ToolNode(tools))
    workflow.add_node("advisor", advisor_agent)
    
    # 添加边
    workflow.set_entry_point("researcher")
    
    # 研究员逻辑
    workflow.add_conditional_edges(
        "researcher",
        should_continue,
        {
            "tools": "tools",
            "advisor": "advisor"
        }
    )
    
    # 工具逻辑
    workflow.add_edge("tools", "researcher")
    
    # 顾问逻辑
    workflow.add_edge("advisor", END)
    
    return workflow.compile()

# 便捷函数
def get_investment_advice(user_assets: UserAssets) -> str:
    """
    使用多 Agent 系统分析用户的投资组合并提供投资建议。
    
    Args:
        user_assets: 包含用户财务数据的 UserAssets 实例。
        
    Returns:
        包含详细投资建议的字符串。
    """
    app = create_multi_agent_graph()
    
    # 使用单个指令初始化状态
    initial_state = {
        "messages": [HumanMessage(content=f"Please analyze {user_assets.user_name}'s portfolio and provide an improvement plan.")],
        "user_assets": str(user_assets)
    }
    
    # 运行图
    result = app.invoke(initial_state)
    
    # Debug: 打印所有消息以检查工具调用
    # for msg in result["messages"]:
    #     print(f"[{msg.type}]: {msg.content}")
    #     if hasattr(msg, 'tool_calls') and msg.tool_calls:
    #         print(f"Tool Calls: {msg.tool_calls}")

    # 返回最后一条消息的内容（来自顾问）
    return result["messages"][-1].content
