import os
import asyncio
from typing import List, Dict
import openpyxl
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from browser_use.agent.service import Agent
from browser_use.browser.browser import Browser, BrowserConfig
import json

load_dotenv()


EXCEL_PATH = "./thevc_invest_list.xlsx"

FIELDS_TO_EXTRACT = [
    "기업 이름", "설립연월", "상세정보", "대표자 정보", "경쟁사 리스트", "상장, 비상장 여부",
    "투자 라운드", "투자 유치 건수", "투자 금액", "임직원수", "회사 홈페이지",
    "제품/서비스 목록", "특허 개수", "등기 임원 수", "AI_관련기업여부", "AI_관련성_설명"
]

def get_company_links_by_category(category_name: str) -> List[Dict]:
    wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
    ws = wb.active
    header_row = [cell.value for cell in ws[1]]  # 1행에서 카테고리 읽기
    print("엑셀 1행(헤더):", header_row)
    try:
        category_col_idx = header_row.index(category_name)
    except ValueError:
        print(f"'{category_name}'이(가) 헤더에 없습니다. 실제 헤더를 확인하세요.")
        raise
    companies = []
    for row_idx, row in enumerate(ws.iter_rows(min_row=2, max_row=ws.max_row), start=2):
        company_name = row[1].value if row[1] else None  # B열(회사명)
        cell = row[category_col_idx]
        link = cell.hyperlink.target if cell.hyperlink else None
        if company_name and link and str(link).startswith("http"):
            companies.append({"company": company_name, "link": link})
    return companies

def build_thevc_prompt(company_name: str, link: str) -> str:
    return f"""
### Prompt for THE VC Company Info Extraction

**Objective:**  
Visit the following company page on THE VC: {link}
Extract and return the following details as JSON:
- "기업 이름"
- "설립연월"
- "상세정보"
- "대표자 정보"
- "경쟁사 리스트"
- "상장, 비상장 여부"
- "투자 라운드"
- "투자 금액"
- "투자 유치 건수"
- "임직원수"
- "회사 홈페이지"
- "제품/서비스 목록"
- "특허 개수"
- "등기 임원 수"
- "AI_관련기업여부"
- "AI_관련성_설명"

**Instructions:**
- For "제품/서비스 목록" and "경쟁사 리스트", return as a list.
- For "상세정보" , return 회사가 어떤 상품을 메인으로 일을 진행하는지 입니다.
- If any field is missing, return "No data".
- For AI_관련기업여부, return only True or False and if it is unknown then it is False.
- Output as JSON with the above keys.e
-use minimum step.
"""

async def fetch_company_info(company: Dict, browser: Browser, llm: ChatOpenAI) -> Dict:
    # 프롬프트에 AI 관련성 판단 요청 추가
    prompt = build_thevc_prompt(company["company"], company["link"])
    agent = Agent(task=prompt, llm=llm, browser=browser)
    history = await agent.run()
    result = history.final_result()
    
    # GPT가 판단한 AI 관련 기업 여부로 필터링
    try:
        print(f"[{company['company']}] result 원본: {result}")        
        result_dict = json.loads(result)
        is_ai_company = result_dict.get("AI_관련기업여부", False)
        if not is_ai_company:
            print(f"[{company['company']}] AI 관련 아님: {result_dict.get('AI_관련성_설명', '')}")
            return {}
        print(f"[{company['company']}] {result}")
        return {company["company"]: result}
    except Exception as e:
        print(f"[{company['company']}] 결과 파싱 오류: {e}")
        return {}

async def process_companies_in_batches(companies: List[Dict], batch_size: int = 10):
    llm = ChatOpenAI(model="gpt-4o")
    results = {}

    # 기업 수가 40개 이상이면 30이상부터만 추출
    if len(companies) >= 50:
        companies = companies[30:35]
    ai_company_count = 0
    processed_companies = []

    for i in range(0, len(companies), batch_size):
        if ai_company_count >= 3:  # 3개의 AI 기업을 찾으면 중단
            break
            
        batch = companies[i:i+batch_size]
        browser = Browser(
                config=BrowserConfig(
                    disable_security=False,
                    headless=False,
                    keep_alive=False,
                    chrome_instance_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',  # macOS path
                    # new_context_config=BrowserContextConfig(save_recording_path='./tmp/recordings')
                ),
                # browser_binary_path = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            )
        # browsers = [
        #     Browser(
        #         config=BrowserConfig(
        #             disable_security=False,
        #             headless=False,
        #             keep_alive=True,
        #             chrome_instance_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        #         )
        #     )
        #     for _ in batch
        # ]
        # tasks = [
        #     fetch_company_info(company, browser, llm)
        #     for company, browser in zip(batch, browsers)
        # ]
        tasks = [
            fetch_company_info(company, browser, llm)
            for company in batch
        ]
        batch_results = await asyncio.gather(*tasks)
        # for browser in browsers:
        #     print("browser close")
        #     await browser.close()
        print("browser close")
        await browser.close()

        for res in batch_results:
            if res:  # 빈 딕셔너리가 아닌 경우(AI 기업인 경우)만 처리
                results.update(res)
                ai_company_count += 1
                if ai_company_count >= 5:
                    break
                    
    return results

def main(category_name: str):
    companies = get_company_links_by_category(category_name)
    print(f"Found {len(companies)} companies in category '{category_name}'")
    results = asyncio.run(process_companies_in_batches(companies, batch_size=5))
    print("All results:")
    for company, info in results.items():
        print(f"\n[{company}]\n{info}\n")

if __name__ == "__main__":
    # Example usage: change "AI" to your desired category
    main("음식/외식")