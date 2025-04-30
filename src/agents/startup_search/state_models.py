from pydantic import BaseModel
from typing import List, Optional

class StartupSearchInput(BaseModel):
    sector_keyword: str

class StartupSearchOutput(BaseModel):
    기업_이름: str
    설립연월: Optional[str]
    상세정보: Optional[str]
    대표자_정보: Optional[str]
    경쟁사_리스트: List[str]
    상장_비상장_여부: Optional[str]
    투자_라운드: Optional[str]
    투자_유치_건수: Optional[int]
    투자_금액: Optional[float]
    임직원수: Optional[int]
    회사_홈페이지: Optional[str]
    제품_서비스_목록: List[str]
    특허_개수: Optional[int]
    등기_임원_수: Optional[int]
    AI_관련기업여부: Optional[bool]
    AI_관련성_설명: Optional[str]


from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class StartupSearchState(BaseModel):
    # 입력 키워드
    sector_keyword: str

    # 중간 상태: 엑셀에서 읽어온 회사 리스트
    companies: Optional[List[Dict[str, str]]] = None

    # 최종 결과: AI 관련 기업 JSON 맵핑
    results: Optional[Dict[str, Any]] = None
