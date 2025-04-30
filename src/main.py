# src/main.py

from agents.startup_search.graph_builder import build_graph as build_startup_graph
from agents.startup_search.state_models import StartupSearchState
# TODO: 실제 구현 후 아래 import 경로 수정
# from agents.tech_summary.graph_builder import build_graph as build_tech_graph
# from agents.tech_summary.state_models import TechSummaryState
# from agents.market_evaluation.graph_builder import build_graph as build_market_graph
# from agents.market_evaluation.state_models import MarketEvaluationState
# ... 나머지 에이전트 import
import asyncio

def main():
    # 1) 사용자로부터 카테고리 키워드 입력
    keyword = input("카테고리 입력> ").strip()

    # ──────────────────────────────────────────────────────
    # 2) 🔍 스타트업 탐색 에이전트 실행
    startup_graph = build_startup_graph()
    startup_state = StartupSearchState(sector_keyword=keyword)
    raw_result = asyncio.run(startup_graph.ainvoke(startup_state))
    final_state = StartupSearchState(**raw_result)  # dict → pydantic 모델로 변환
    companies_info = final_state.results or {}


    # ──────────────────────────────────────────────────────
    # 3) 🗜️ 기술 요약 에이전트 실행 (예시)
    # tech_graph = build_tech_graph()
    # tech_results = {}
    # for name, company_output in companies_info.items():
    #     tech_input_state = TechSummaryState(
    #         company_name=name,
    #         company_info=company_output
    #     )
    #     tech_final = tech_graph.invoke(tech_input_state)
    #     tech_results[name] = tech_final.summary
    # print(f"[2️⃣ 기술 요약 완료]")

    # ──────────────────────────────────────────────────────
    # 4) 📊 시장성 평가 에이전트 실행 (예시)
    # market_graph = build_market_graph()
    # market_results = {}
    # for name, tech_summary in tech_results.items():
    #     market_input_state = MarketEvaluationState(
    #         company_name=name,
    #         tech_summary=tech_summary
    #     )
    #     market_final = market_graph.invoke(market_input_state)
    #     market_results[name] = market_final.metrics
    # print(f"[3️⃣ 시장성 평가 완료]")

    # ──────────────────────────────────────────────────────
    # TODO: 👤 창업자 평가, 🥊 경쟁사 비교, 🧮 투자 판단, 📝 보고서 생성 에이전트도
    #     위와 똑같은 패턴으로 build_graph() → invoke() 순서로 연결

    # ──────────────────────────────────────────────────────
    # 예시 출력 (현재는 스타트업 탐색 결과만)
    print("\n===== 최종 결과 (현재: 스타트업 탐색) =====")
    for comp, info in companies_info.items():
        print(f"\n[{comp}]\n{info.json(indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    main()
