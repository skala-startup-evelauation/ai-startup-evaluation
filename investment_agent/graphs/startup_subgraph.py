from langgraph import Graph, LLMChainNode
from models.startup import Startup

def make_startup_subgraph() -> Graph:
    g = Graph(name="StartupSubgraph")
    g.add_input("startup", Startup)
    
    # 1-1) 시장성 지표 주입 (이미 받아왔으면 건너뛸 수 있음)
    g.add_node(
        LLMChainNode("MarketAgent", prompt="…"),
        inputs={"startup": "startup"},
        outputs={"startup": "startup"},
    )
    # 1-2) 기술 요약 채우기
    g.add_node(
        LLMChainNode("TechSummaryAgent", prompt="…"),
        inputs={"startup": "startup"},
        outputs={"startup": "startup"},
    )
    # 1-3) 경쟁사 비교
    g.add_node(
        LLMChainNode("CompetitorComparisonAgent", prompt="…"),
        inputs={"startup": "startup"},
        outputs={"startup": "startup"},
    )
    # 1-4) 창업자 평가
    g.add_node(
        LLMChainNode("FounderEvalAgent", prompt="…"),
        inputs={"startup": "startup"},
        outputs={"startup": "startup"},
    )
    
    g.set_output("startup")
    return g
