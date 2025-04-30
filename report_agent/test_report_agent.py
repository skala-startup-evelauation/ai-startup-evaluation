# test_report_agent.py
# ReportLab을 사용한 투자 보고서 생성 테스트

from report_agent import ReportLabReportAgent
from datetime import datetime

# ReportLab 보고서 에이전트 초기화
report_agent = ReportLabReportAgent(
    output_dir="reports",                      # 보고서 저장 디렉토리
    company_logo=None,                         # 로고는 생략 (선택적)
    font_path=None,                            # 폰트 경로 (자동 검색)
    color_scheme={                             # 커스텀 색상 스키마 (선택적)
        "primary": "#1a73e8",                 # 주 색상 (파란색)
        "secondary": "#34a853",               # 보조 색상 (녹색)
        "accent": "#ea4335",                  # 강조 색상 (빨간색)
        "neutral": "#5f6368",                 # 중립 색상 (회색)
        "background": "#f8f9fa",              # 배경 색상 (밝은 회색)
        "text_primary": "#202124",            # 주 텍스트 색상 (검정색)
        "text_secondary": "#5f6368",          # 보조 텍스트 색상 (회색)
        "success": "#34a853",                 # 성공 색상 (녹색)
        "warning": "#fbbc04",                 # 경고 색상 (노란색)
        "danger": "#ea4335"                   # 위험 색상 (빨간색)
    }
)

# 샘플 데이터
startup_data = {
    "name": "테크스타트업",
    "description": "AI 기반 핀테크 솔루션 제공 기업"
}

market_analysis = {
    "market_size": "10조원",
    "growth_rate": 15.0,
    "score": 85.0,
    "summary": "AI 기반 핀테크 시장은 연평균 15% 성장 중이며, 디지털 전환 가속화로 향후 시장 성장이 유망함."
}

tech_analysis = {
    "tech_stack": ["딥러닝 기반 신용평가 알고리즘", "빅데이터 처리 시스템"],
    "score": 80.0,
    "summary": "독자적인 AI 기술력을 보유하고 있으며, 3건의 특허로 기술 경쟁력을 확보했으나 시스템 확장성 검증이 필요함."
}

competitor_analysis = {
    "main_competitors": ["핀테크 대기업 A", "기술 스타트업 B", "해외 핀테크 C"],
    "market_share": {
        "핀테크 대기업 A": 35.0,
        "기술 스타트업 B": 25.0,
        "해외 핀테크 C": 15.0,
        "테크스타트업": 10.0,
        "기타": 15.0
    },
    "summary": "시장 점유율은 낮지만 기술력에서 경쟁 우위를 확보하고 있음."
}

founder_analysis = {
    "experience": "금융업 15년 경력",
    "expertise": "금융공학 전문가",
    "score": 90.0,
    "summary": "주요 창업자는 금융업 15년 경력과 핀테크 분야의 전문성을 갖추고 있어 시장과 기술에 대한 이해도가 높음."
}

investment_decision = {
    "decision": "투자",
    "confidence": 80.0,
    "reasons": [
        "기술력 우수 및 특허 보유",
        "시장 성장성 높음",
        "창업자의 전문성과 경험 검증됨"
    ]
}

# 단일 보고서 생성
print("단일 투자 보고서 생성 시작...")

result = report_agent.generate_report(
    startup_data=startup_data,
    market_analysis=market_analysis,
    tech_analysis=tech_analysis,
    competitor_analysis=competitor_analysis,
    founder_analysis=founder_analysis,
    investment_decision=investment_decision,
    output_pdf_path="reports/테크스타트업_투자보고서.pdf"  # 파일 경로 지정
)

if result["pdf_path"]:
    print(f"PDF 보고서 생성 완료: {result['pdf_path']}")
else:
    print("PDF 보고서 생성 실패")