'''
investment_agent_system/
└── investment_agent/
    ├── graphs/
    │   ├── pipeline.py            # 투자 평가 메인 그래프
    │   └── startup_subgraph.py    # 기업별 서브그래프 정의
    ├── agents/                    # LangGraph용 에이전트 래퍼(설계된 파이프라인 기반 예시, 마음대로 추가 및 수정 가능)
    │   ├── exploration_agent.py
    │   ├── market_agent.py
    │   ├── tech_summary_agent.py
    │   ├── competitor_agent.py
    │   ├── founder_eval_agent.py
    │   ├── investment_judgment_agent.py
    │   └── report_generation_agent.py
    ├── models/                    # Pydantic 스키마
    │   └── startup.py
    └── main.py                    # pipeline.run() 호출 스크립트
'''