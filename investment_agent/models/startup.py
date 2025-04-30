# investment_agent/models/startup.py

from typing import List, Optional
from datetime import date
from pydantic import BaseModel, HttpUrl

class FundingRound(BaseModel):
    round_name: str
    date: Optional[date]
    amount_usd: Optional[float]
    lead_investor: Optional[str]

class MarketMetrics(BaseModel):
    tam_usd: Optional[float]
    sam_usd: Optional[float]
    som_usd: Optional[float]
    cagr: Optional[float]
    competitive_intensity: Optional[str]

class Financials(BaseModel):
    burn_rate_usd_per_month: Optional[float]
    runway_months: Optional[int]
    last_3y_revenue: Optional[List[float]]

class FounderInfo(BaseModel):
    name: str
    education: Optional[str]
    career: Optional[str]
    risk_factors: Optional[str]
    key_strengths: Optional[str]

class Startup(BaseModel):
    name: str
    founded_at: Optional[date]
    description: Optional[str]
    founder: Optional[FounderInfo]
    competitors: List[str] = []
    is_listed: Optional[bool]
    funding_rounds: List[FundingRound] = []
    total_investments: Optional[int]
    employee_count: Optional[int]
    website: Optional[HttpUrl]
    products_services: List[str] = []
    patent_count: Optional[int]
    board_member_count: Optional[int]
    market_metrics: Optional[MarketMetrics]
    financials: Optional[Financials]
