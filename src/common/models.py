from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import date

class FundingRound(BaseModel):
    round_name: str
    date: Optional[date] = None
    amount_usd: Optional[float] = None
    lead_investor: Optional[str] = None

class MarketMetrics(BaseModel):
    tam_usd: Optional[float] = None
    sam_usd: Optional[float] = None

class CompanyState(BaseModel):
    sector_keyword: str
    funding: Optional[FundingRound] = None
    metrics: Optional[MarketMetrics] = None
