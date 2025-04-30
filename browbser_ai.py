import asyncio
import json
from langchain_openai import ChatOpenAI
from browser_use import Agent, Browser, BrowserConfig
from dotenv import load_dotenv
load_dotenv()

from pydantic import BaseModel
# Define the output format as a Pydantic model
class Product(BaseModel):
    name: str
    image_url: str
    link: int
    rating: str
    reviews: str


class Products(BaseModel):
	Products: list[Product]

async def search_coupang_item_browser(item_name: str) -> dict:
    """
    browser-use를 활용하여 쿠팡에서 주어진 제품(item_name)을 검색한 후,
    최상위 결과의 제품명, 이미지 링크, 상품 링크를 JSON 형식으로 반환합니다.
    
    **출력 예시 (JSON):**
    {
      "name": "제품명",
      "image_url": "https://...",
      "link": "https://...",
      "rating": "4.5",
      "reviews": "123"
    }
    
    만약 검색 결과가 없다면 각 값은 "No results found"로 반환합니다.
    """
    # browser 인스턴스 생성 - 유저 브라우저 생성
    browser = Browser(
        config=BrowserConfig(
        # Specify the path to your Chrome executable
        chrome_instance_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',  # macOS path
        # For Windows, typically: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
        # For Linux, typically: '/usr/bin/google-chrome'
    )
    )
    
    # task 프롬프트 정의 (JSON 형식으로 결과 반환하도록 요청)
    task = f"""
### Prompt for Supplement Search on Coupang

**Objective:**  
Visit [coupang](https://coupang.com/), search for the product "{item_name}", and return the following details as JSON:
- "name": Product Name
- "image_url": Product Image URL
- "link": Product URL

**Instructions:**
- Use the search bar on coupang to search for "{item_name}".
- Select the top result.
- Do not add the product to the cart or proceed with checkout.
- If no product is found, return a JSON object with all values as "No results found".

**Output Format:**
Return a JSON object exactly as follows:
{{"name": "...", "image_url": "...", "link": "...", "rating": "4.5", "reviews": "123"}}  
    """
    
    # LLM 설정 (GPT-4o 사용)
    llm = ChatOpenAI(model="gpt-4o")
    
    # Agent 생성
    agent = Agent(
        task=task,
        llm=llm,
        browser=browser,
    )
    
        # Agent 실행
    history = await agent.run()

    result = history.final_result()
    if result:
            print("result3322: ", result)
            parsed: Products = Products.model_validate_json(result)
            for product in parsed.Products:
                print(product.name, product.image_url, product.link, product.rating, product.reviews)
    
    outputs = parsed.Products
    # print(result)
    # 브라우저 종료
    await browser.close()
    

    return outputs



def search_coupang_item_browser_sync(item_name: str) -> dict:
    """비동기 함수를 동기식으로 실행하기 위한 래퍼 함수"""
    return asyncio.run(search_coupang_item_browser(item_name))

# 쿠팡에서 '아이패드' 검색 결과 반환
# search_coupang_item_browser_sync("아이패드")


# Define the output format as a Pydantic model
class NewsArticle(BaseModel):
    title: str
    summary: str
    url: str
    image_url: str
    date: str

class NewsArticles(BaseModel):
    articles: list[NewsArticle]

async def search_news_browser(keyword: str) -> list[NewsArticle]:
    """
    Uses browser-use to search for news articles related to the given keyword.
    Returns a list of news articles (title, summary, url, image_url, date) as JSON.
    If no results, returns a single article with all fields as "No results found".
    """
    browser = Browser(
        config=BrowserConfig(
            chrome_instance_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        )
    )

    task = f"""
### Prompt for News Search

**Objective:**  
Visit a major news portal (e.g., Naver News, Google News, or Daum News), search for "{keyword}", and return the following details for the top 3 news articles as JSON:
- "title": Article Title
- "summary": Short summary or snippet
- "url": Article URL
- "image_url": Main image URL (if available)
- "date": Publication date

**Instructions:**
- Use the search bar to search for "{keyword}".
- Select the top 3 news articles.
- If no articles are found, return a JSON array with one object where all values are "No results found".

**Output Format:**
Return a JSON object exactly as follows:
{{"articles": [{{"title": "...", "summary": "...", "url": "...", "image_url": "...", "date": "..."}}]}}
    """

    llm = ChatOpenAI(model="gpt-4o")
    agent = Agent(
        task=task,
        llm=llm,
        browser=browser,
    )

    history = await agent.run()
    result = history.final_result()
    if result:
        print("news_result: ", result)
        parsed: NewsArticles = NewsArticles.model_validate_json(result)
        for article in parsed.articles:
            print(article.title, article.summary, article.url, article.image_url, article.date)
        outputs = parsed.articles
    else:
        outputs = [NewsArticle(
            title="No results found",
            summary="No results found",
            url="No results found",
            image_url="No results found",
            date="No results found"
        )]
    await browser.close()
    return outputs

def search_news_browser_sync(keyword: str) -> list[NewsArticle]:
    """Runs the async news search synchronously."""
    return asyncio.run(search_news_browser(keyword))

# Example: Search for news about '아이패드'
# search_news_browser_sync("아이패드")


# Define the output format as a Pydantic model for VC investment info
class VCInvestment(BaseModel):
    company: str
    round: str
    amount: str
    date: str
    investors: str
    link: str

class VCInvestments(BaseModel):
    investments: list[VCInvestment]

async def search_vc_investment_browser(keyword: str) -> list[VCInvestment]:
    """
    Uses browser-use to search for VC investment information related to the given keyword.
    Returns a list of investments (company, round, amount, date, investors, link) as JSON.
    If no results, returns a single investment with all fields as "No results found".
    """
    browser = Browser(
        config=BrowserConfig(
            chrome_instance_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        )
    )

    task = f"""
### Prompt for VC Investment Search

**Objective:**  
Visit a major VC/Startup investment database (e.g., TheVC), search for "{keyword}", and return the following details for the top 3 recent investments as JSON:
- "company": Company Name
- "round": Investment Round (e.g., Series A, Seed)
- "amount": Investment Amount
- "date": Investment Date
- "investors": Main Investors
- "link": Link to the investment or company profile

**Instructions:**
- Use the search bar to search for "{keyword}".
- Select the top 3 most recent investments.
- If no investments are found, return a JSON array with one object where all values are "No results found".

**Output Format:**
Return a JSON object exactly as follows:
{{"investments": [{{"company": "...", "round": "...", "amount": "...", "date": "...", "investors": "...", "link": "..."}}]}}
    """

    llm = ChatOpenAI(model="gpt-4o")
    agent = Agent(
        task=task,
        llm=llm,
        browser=browser,
    )

    history = await agent.run()
    result = history.final_result()
    if result:
        print("vc_result: ", result)
        parsed: VCInvestments = VCInvestments.model_validate_json(result)
        for inv in parsed.investments:
            print(inv.company, inv.round, inv.amount, inv.date, inv.investors, inv.link)
        outputs = parsed.investments
    else:
        outputs = [VCInvestment(
            company="No results found",
            round="No results found",
            amount="No results found",
            date="No results found",
            investors="No results found",
            link="No results found"
        )]
    await browser.close()
    return outputs

def search_vc_investment_browser_sync(keyword: str) -> list[VCInvestment]:
    """Runs the async VC investment search synchronously."""
    return asyncio.run(search_vc_investment_browser(keyword))

# Example: Search for VC investments about '아이패드'
search_vc_investment_browser_sync("아이패드")