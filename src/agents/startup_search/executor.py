from .graph_builder import build_graph
from .state_models import StartupSearchState

def main(keyword: str):
    graph = build_graph()
    init_state = StartupSearchState(sector_keyword=keyword)
    final_state = graph.invoke(init_state)
    # 결과 매핑: {기업명: StartupSearchOutput}
    return final_state.results or {}

if __name__ == "__main__":
    res = main("음식/외식")
    for comp, info in res.items():
        print(f"\n[{comp}]\n{info.json(indent=2, ensure_ascii=False)}")
