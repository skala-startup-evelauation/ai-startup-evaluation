from langgraph.graph import StateGraph
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from browse_thevc import main as browse_thevc_main, process_companies_in_batches, get_company_links_by_category

# 한글 → 영어 key 매핑
KOR2ENG = {
    "기업 이름": "company_name",
    "설립연월": "established_date",
    "상세정보": "description",
    "대표자 정보": "ceo_info",
    "경쟁사 리스트": "competitors",
    "상장, 비상장 여부": "listing_status",
    "투자 라운드": "investment_round",
    "투자 유치 건수": "investment_count",
    "투자 금액": "investment_amount",
    "임직원수": "employee_count",
    "회사 홈페이지": "homepage",
    "제품/서비스 목록": "products_services",
    "특허 개수": "patent_count",
    "등기 임원 수": "registered_executives",
    "AI_관련기업여부": "is_ai_company",
    "AI_관련성_설명": "ai_relevance_desc"
}

def kor2eng_keys(result_json_str):
    """한글 key를 영어 key로 변환"""
    try:
        data = json.loads(result_json_str)
        return {KOR2ENG.get(k, k): v for k, v in data.items()}
    except Exception as e:
        print("JSON 변환 오류:", e)
        return {}

def fetch_and_translate(category_name: str):
    companies = get_company_links_by_category(category_name)
    results = asyncio.run(process_companies_in_batches(companies, batch_size=5))
    translated = {}
    for company, info in results.items():
        translated[company] = kor2eng_keys(info)
    print(json.dumps(translated, ensure_ascii=False, indent=2))
    return translated

# StateGraph 정의
graph = StateGraph(name="BrowseTheVCStateGraph")
graph.add_input("category_name", str)
graph.add_state("translated_results", dict)

graph.add_node(
    PythonNode(
        name="FetchAndTranslateNode",
        function=fetch_and_translate
    ),
    inputs={"category_name": "category_name"},
    outputs={"translated_results": "translated_results"}
)
graph.set_output("translated_results")

if __name__ == "__main__":
    category = input("카테고리명을 입력하세요 (예: 음식/외식): ").strip()
    result = graph.run({"category_name": category})
    print(json.dumps(result["translated_results"], ensure_ascii=False, indent=2))