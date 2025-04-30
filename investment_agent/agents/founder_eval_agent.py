# investment_agent/agents/founder_eval_agent.py

import os
import json
from typing import Optional, List, Dict
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv  # dotenv 먼저 import
from startup import FounderInfo



# 1. 환경 변수 로딩
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if api_key is None:
    raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")

client = OpenAI(api_key=api_key)

# 2. GPT 질의 함수
def ask_gpt(question: str, system_msg: str = "아래 질문에 대해 한국어로 간단히 대답해 주세요.") -> str:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": question}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()


def evaluate_founder(startup_name: str, founder_name: Optional[str]) -> FounderInfo:
    if founder_name is None:
        founder_name = ask_gpt(f"{startup_name}의 창업자 이름은 누구인가요?")

    print(f"{startup_name} 창업자 '{founder_name}'에 대한 정보 수집 중...")

    # 질문 목록
    questions = {
        "education": f"{startup_name}의 창업자 {founder_name}의 최종 학력은 무엇이며, 어떤 학교에서 어떤 전공을 공부했나요?",
        "career": f"{startup_name}의 창업자 {founder_name}는 창업 전 어떤 회사에서 어떤 직책으로 근무했으며, 각 경력의 기간과 주요 성과는 무엇인가요?",
        "risk_factors": f"{startup_name}의 창업자 {founder_name}에게 실패한 창업 경험, 논란, 법적 문제 등 리스크 요인이 있었다면 구체적으로 설명해주세요.",
        "key_strengths": f"{startup_name}의 대표 {founder_name}의 기술적/사업적 강점과 리더십이나 글로벌 진출 능력 등 두드러진 역량을 알려주세요."
    }

    # GPT 응답 수집
    responses = {}
    for key, question in questions.items():
        if key not in responses:  # 이미 저장된 key는 건너뛰기 (중복 방지)
            print(f"→ GPT 질문: {question}")
            responses[key] = ask_gpt(question)

    return FounderInfo(
        name=founder_name,
        education=responses["education"],
        career=responses["career"],
        risk_factors=responses["risk_factors"],
        key_strengths=responses["key_strengths"]
    )

