# scripts/test_invest_judgement.py

import sys, os, json
from datetime import date
from typing import TypedDict, List
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END

# 프로젝트 루트를 PYTHONPATH에 추가
ROOT = os.path.abspath(os.path.join(__file__, os.pardir, os.pardir))
sys.path.insert(0, ROOT)

# 1) Pydantic 모델 import
from models.startup import (
    Startup, FounderInfo, MarketMetrics, Financials, FundingRound
)

# 에이전트 인스턴스 import
from agents.investment_judgement_agent import investment_judgement_agent

# 그래프 상태 스키마: 반드시 JSON-serializable 타입만!
class GraphState(TypedDict):
    # 입력: Pydantic 모델을 JSON으로 덤프한 dict
    startups:        List[dict]
    # 출력: ranked_startups 역시 dict 리스트
    ranked_startups: List[dict]

# StateGraph 생성
graph = StateGraph(GraphState)

# 노드 정의: state → agent 호출 → dict 리스트 반환
def _run_agent(state: GraphState) -> dict:
    # a) dict → Startup 객체 복원
    objs = [ Startup.model_validate(d) for d in state["startups"] ]
    # b) 에이전트 실행 (Startup 인스턴스 리스트 반환)
    result = investment_judgement_agent(objs)
    # c) 결과 Startup → 순수 dict (JSON 호환) 변환
    ranked = [
        s.model_dump(mode="json", exclude_none=True)
        for s in result["ranked_startups"]
    ]
    return {"ranked_startups": ranked}

# 6) 노드·엣지 연결
graph.add_node("InvestmentJudgmentAgent", _run_agent)
graph.add_edge(START, "InvestmentJudgmentAgent")
graph.add_edge("InvestmentJudgmentAgent", END)

# # 초기 입력 준비: model_dump(mode="json") 로 date→"YYYY-MM-DD" 직렬화
# input_dict = {
#     "startups": [
#         s.model_dump(mode="json", exclude_none=True)
#         for s in (startup1, startup2, startup3)
#     ]
# }

# # 8) 실행
# app    = graph.compile()
# output = app.invoke(input_dict)

# # 9) 결과 출력
# print("== Ranked Startups ==")
# for i, d in enumerate(output["ranked_startups"], 1):
#     print(f"{i}. {d['name']} (Score: {d['total_score']:.2f})")
#     print(f"   Qual: {d['qualitative_assessment']}")
#     print(f"   Scores: {d['scores']}")
#     print()