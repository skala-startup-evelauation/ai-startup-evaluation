import os
from typing import Optional, Dict, Any, List
from openai import OpenAI
from dotenv import load_dotenv
from investment_agent.models.startup import FounderInfo, Startup

# 1. 환경 변수 로딩
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if api_key is None:
    raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")

client = OpenAI(api_key=api_key)

# 2. 🔍 MOCK: 백그라운드 정보 검색 함수 (벡터 DB 대체용)
def search_background_info(startup_name: str) -> List[str]:
    # TODO: 실제 RAG 벡터 검색으로 대체 가능
    return [
        f"{startup_name}은 인공지능 기반 헬스케어 솔루션을 제공하며, 최근 시리즈B 투자를 유치했습니다.",
        f"창업자는 MIT 출신으로 머신러닝 연구 경력이 있으며, 글로벌 학회 발표 경력이 있습니다.",
        f"과거 실패한 스타트업 경험이 있었으나, 현재 창업에서는 안정적 성장세를 보이고 있습니다."
    ]

# 3. 🔄 백그라운드 요약 생성
def generate_background_summary(docs: List[str]) -> str:
    joined_context = "\n".join(docs)
    system_msg = "다음 배경 정보들을 간결하게 요약해 주세요. 한국어로 3~4문장 이내로 작성해주세요."
    return ask_gpt(joined_context, system_msg)

# 4. GPT 질의 함수
def ask_gpt(question: str, system_msg: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": question}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

# 5. LangGraph용 노드 함수
def evaluate_founder_node(inputs: Dict[str, Any]) -> Dict[str, Any]:
    startup: Startup = inputs["startup"]
    founder_name: Optional[str] = startup.founder.name if startup.founder else None
    startup_name: str = startup.name

# 단일 실행용 evaluate 함수
# def evaluate_founder(startup_name: str, founder_name: Optional[str]) -> FounderInfo:
#     if founder_name is None:
#         founder_name = ask_gpt(f"{startup_name}의 창업자 이름은 누구인가요?")

    # 🔍 백그라운드 문서 검색 및 요약
    background_docs = search_background_info(startup_name)
    background_summary = generate_background_summary(background_docs)

    print(f"[{startup_name}] 백그라운드 요약 생성 완료:\n{background_summary}\n")

    # 이름이 없으면 추론
    if not founder_name:
        founder_name = ask_gpt(
            f"{startup_name}의 창업자 이름은 누구인가요?",
            system_msg=f"{background_summary}\n위 정보에 기반하여 질문에 답하세요."
        )

    print(f"{startup_name} 창업자 '{founder_name}'에 대한 정보 수집 중...")

    # 창업자 관련 질문 정의
    questions = {
        "education": f"{startup_name}의 창업자의 최종 학력은 무엇이며, 어떤 학교에서 어떤 전공을 공부했나요?",
        "career": f"{startup_name}의 창업자는 창업 전 어떤 회사에서 어떤 직책으로 근무했으며, 각 경력의 기간과 주요 성과는 무엇인가요?",
        "risk_factors": f"{startup_name}의 창업자에게 실패한 창업 경험, 논란, 법적 문제 등 리스크 요인이 있었다면 구체적으로 설명해주세요.",
        "key_strengths": f"{startup_name}의 대표의 기술적/사업적 강점과 리더십이나 글로벌 진출 능력 등 두드러진 역량을 알려주세요."
    }

    responses = {}
    for key, question in questions.items():
        print(f"→ GPT 질문: {question}")
        responses[key] = ask_gpt(
            question,
            system_msg=f"{background_summary}\n위 배경 정보를 바탕으로 아래 질문에 답하세요."
        )

    # FounderInfo 생성 및 Startup에 주입
    startup.founder = FounderInfo(
        name=founder_name,
        education=responses["education"],
        career=responses["career"],
        risk_factors=responses["risk_factors"],
        key_strengths=responses["key_strengths"]
    )

    return {"startup": startup}
