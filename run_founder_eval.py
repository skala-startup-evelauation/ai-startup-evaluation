# run_founder_eval_langgraph.py

from investment_agent.agents.founder_eval_agent import evaluate_founder_node
from investment_agent.models.startup import Startup, FounderInfo
from langgraph.graph import StateGraph

# 1. Startup 객체 정의
startup = Startup(
    name="배달의민족",
    founder=None,
    founded_at="2010-03-01",
    description="음식 배달 주문 플랫폼 서비스로 국내 대표 O2O 스타트업",
    is_listed=False,
    total_investments=250000000000,
    employee_count=1000,
    website="https://www.baemin.com",
    patent_count=10,
    board_member_count=4,
    market_metrics={
        "monthly_users": 18000000,
        "growth_rate": 0.18,
        "tam_usd": 8000000000,
        "sam_usd": 2000000000,
        "som_usd": 1000000000,
        "cagr": 0.12,
        "competitive_intensity": "Medium"
    },
    financials={
        "revenue": 300000000000,
        "profit": 5000000000,
        "burn_rate_usd_per_month": 4000000,
        "runway_months": 36,
        "last_3y_revenue": [150000000000, 220000000000, 300000000000]
    }
)

# 2. LangGraph 워크플로우 구성
builder = StateGraph()
builder.add_node("founder_eval", evaluate_founder_node)
builder.set_entry_point("founder_eval")
graph = builder.compile()

# 3. 실행
result = graph.invoke({"startup": startup})

# 4. 결과 출력
founder: FounderInfo = result["startup"].founder

print("\n📌 LangGraph 실행 결과:")
print(f"창업자 이름: {founder.name}")
print(f"학력: {founder.education}")
print(f"경력: {founder.career}")
print(f"리스크 요인: {founder.risk_factors}")
print(f"주요 강점: {founder.key_strengths}")
