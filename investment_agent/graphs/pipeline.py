from langgraph import Graph, LLMChainNode, MapNode
from graphs.startup_subgraph import make_startup_subgraph

pipeline = Graph(name="InvestmentPipeline")
pipeline.add_input("industry_keyword", str)

pipeline.add_node(
    LLMChainNode(
        name="ExplorationAgent",
        prompt="Input: {industry_keyword} → Output: startup_list"
    ),
    inputs={"industry_keyword": "industry_keyword"},
    outputs={"startup_list": "startup_list"},
)

pipeline.add_node(
    MapNode(
        source="startup_list",
        element="company_name",
        graph=make_startup_subgraph(),
        inputs_map={"startup": "company_name"},
        outputs_map={"startup": "processed_startup"},
    ),
    outputs={"processed_startups": "processed_startups"},
)

pipeline.add_node(
    LLMChainNode("InvestmentJudgmentAgent", prompt="…"),
    inputs={"startups": "processed_startups"},
    outputs={"ranked_startups": "ranked_startups"},
)

pipeline.add_node(
    LLMChainNode("ReportGenerationAgent", prompt="…"),
    inputs={"startup": ("ranked_startups", 0)},
    outputs={"report": "report"},
)

pipeline.set_output("report")
