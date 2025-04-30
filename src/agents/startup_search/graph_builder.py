import os
import json
import asyncio
import openpyxl
from typing import List, Dict, Any

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from browser_use.agent.service import Agent
from browser_use.browser.browser import Browser, BrowserConfig

from langgraph.graph import StateGraph, END

from .config import EXCEL_PATH, FIELDS_TO_EXTRACT
from .state_models import StartupSearchState, StartupSearchOutput

load_dotenv()

def get_company_links_by_category(category_name: str) -> List[Dict[str, str]]:
    wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
    ws = wb.active
    headers = [cell.value for cell in ws[1]]
    if category_name not in headers:
        raise RuntimeError(f"'{category_name}'이(가) 헤더에 없습니다.")
    idx = headers.index(category_name)
    companies = []
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
        name = row[1].value
        link = row[idx].hyperlink.target if row[idx].hyperlink else None
        if name and link and str(link).startswith("http"):
            companies.append({"company": name, "link": link})
    return companies


def build_thevc_prompt(company_name: str, link: str) -> str:
    return f"""
### THE VC 회사 정보 추출

Objective:
- THE VC 페이지 방문: {link}
- 아래 필드를 JSON 으로 추출하시오: {FIELDS_TO_EXTRACT}

Instructions:
- '경쟁사 리스트', '제품/서비스 목록'은 리스트로
- 없는 필드는 \"No data\"
- For "상세정보" , return 회사가 어떤 서비스를 메인으로 진행하는지 입니다.
- 'AI_관련기업여부'는 True/False
Output: JSON
"""


async def fetch_company_info(
    company: Dict[str, str],
    browser: Browser,
    llm: ChatOpenAI
) -> Dict[str, Any]:
    prompt = build_thevc_prompt(company["company"], company["link"])
    agent = Agent(task=prompt, llm=llm, browser=browser)
    history = await agent.run()
    raw = history.final_result()
    try:
        data = json.loads(raw)
        if not data.get("AI_관련기업여부", False):
            return {}  # AI 기업이 아니면 무시
        # Pydantic 으로 파싱
        output = StartupSearchOutput.parse_obj(data)
        return {company["company"]: output}
    except Exception:
        return {}


async def process_companies_in_batches(
    companies: List[Dict[str, str]],
    batch_size: int = 10
) -> Dict[str, StartupSearchOutput]:
    llm = ChatOpenAI(model="gpt-4o")
    results: Dict[str, StartupSearchOutput] = {}
    ai_count = 0

    # 50개 이상이면 30~35번만 사용
    if len(companies) >= 50:
        companies = companies[30:35]

    for i in range(0, len(companies), batch_size):
        if ai_count >= 3:
            break
        batch = companies[i : i + batch_size]
        # browser = Browser(
        #     config=BrowserConfig(
        #         disable_security=False,
        #         headless=False,
        #         keep_alive=False,
        #         chrome_instance_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',  # macOS path
        #     )
        # )
        # tasks = [fetch_company_info(c, browser, llm) for c in batch]
        browsers = [
            Browser(
                config=BrowserConfig(
                    disable_security=False,
                    headless=False,
                    keep_alive=True,
                    chrome_instance_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                )
            )
            for _ in batch
        ]
        tasks = [
            fetch_company_info(company, browser, llm)
            for company, browser in zip(batch, browsers)
        ]
        batch_res = await asyncio.gather(*tasks)
        # await browser.close()
        for browser in browsers:
            print("browser close")
            await browser.close()
        for entry in batch_res:
            if entry:
                # mapping {name: StartupSearchOutput}
                results.update(entry)
                ai_count += 1
                if ai_count >= 5:
                    break

    return results

def build_graph():
    builder = StateGraph(StartupSearchState)

    # 1) 엑셀에서 링크 읽기
    def read_links(state: StartupSearchState):
        state.companies = get_company_links_by_category(state.sector_keyword)
        return state
    
    # 2) 비동기 LLM+브라우저 처리 → AI 기업만 필터링
    async def fetch_and_filter(state: StartupSearchState):
        state.results = await process_companies_in_batches(state.companies or [], batch_size=5)
        return state

    builder.add_node("read_links", read_links)
    builder.add_node("fetch_and_filter", fetch_and_filter)

    builder.set_entry_point("read_links")
    builder.add_edge("read_links", "fetch_and_filter")
    builder.add_edge("fetch_and_filter", END)

    return builder.compile()
