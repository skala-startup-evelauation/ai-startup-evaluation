from investment_agent.agents.founder_eval_agent import evaluate_founder_node
from investment_agent.models.startup import Startup, FounderInfo

# ▶️ 창업자 이름을 알고 있다면 여기 입력
manual_founder_name = "김봉진"  # 또는 None

startup = Startup(
    name="배달의민족",
    founder=FounderInfo(
        name=manual_founder_name,
        education=None,
        career=None,
        risk_factors=None,
        key_strengths=None
    ) if manual_founder_name else None,
    founded_at="2010-03-01",
    description="음식 배달 주문 플랫폼 서비스로 국내 대표 O2O 스타트업",
    is_listed=False,
    total_investments=250000000000,  # 약 2,500억 원
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

# ▶️ LangGraph 함수 실행
outputs = evaluate_founder_node({"startup": startup})

# ▶️ 결과 출력
result: Startup = outputs["startup"]
founder: FounderInfo = result.founder

print("\n✅ 최종 결과:")
print(f"창업자 이름: {founder.name}")
print(f"학력: {founder.education}")
print(f"경력: {founder.career}")
print(f"리스크 요인: {founder.risk_factors}")
print(f"주요 강점: {founder.key_strengths}")
