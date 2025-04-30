import logging
import requests
from typing import List, Dict, Any


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
        logger.addHandler(ch)
    return logger


def http_get(url: str, params: Dict[str, Any] = None, headers: Dict[str, str] = None) -> Any:
    """
    단순 HTTP GET 요청. JSON 응답을 반환.
    """
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response.json()


def rag_retrieve(sources: List[str], query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    멀티 소스 RAG 검색 placeholder 함수
    실제 구현 시, 각 소스 API 호출 및 결과 통합 로직 필요
    """
    results: List[Dict[str, Any]] = []
    for src in sources:
        # TODO: 각 소스별 검색 로직 구현
        pass
    # 상위 top_k만 반환
    return results[:top_k]
