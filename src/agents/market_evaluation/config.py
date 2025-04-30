import os
from dotenv import load_dotenv

load_dotenv()

# 엑셀 파일 경로
EXCEL_PATH = os.getenv("THE_VC_EXCEL_PATH", "./thevc_invest_list.xlsx")

# 최종 JSON 으로 뽑아낼 필드 리스트
FIELDS_TO_EXTRACT = [
    "기업 이름", "설립연월", "상세정보", "대표자 정보", "경쟁사 리스트", "상장, 비상장 여부",
    "투자 라운드", "투자 유치 건수", "투자 금액", "임직원수", "회사 홈페이지",
    "제품/서비스 목록", "특허 개수", "등기 임원 수", "AI_관련기업여부", "AI_관련성_설명"
]
