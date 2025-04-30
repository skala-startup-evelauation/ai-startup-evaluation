import json
import os

from typing import List, Dict, Any
from pathlib import Path

from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import BaseRetriever
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS

from models.startup import Startup
from config import API_KEY

os.environ["OPENAI_API_KEY"] = API_KEY

class InvestmentJudgmentAgent:
    def __init__(self, index_dir: str):
        # Embedding + FAISS retriever
        embedder = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        vectorstore = FAISS.load_local(
            index_dir,
            embedder,
            allow_dangerous_deserialization=True
        )
        self.retriever: BaseRetriever = vectorstore.as_retriever()

        # Qualitative assessment prompt
        qual_prompt = PromptTemplate(
            input_variables=["company", "context"],
            template=(
                'PDF 기준을 참고하여, 스타트업 "{company}"이 투자할 가치가 있는지 간결히 판단하세요:'
                "\n\n{context}"
            )
        )
        self.qual_chain = LLMChain(
            llm=ChatOpenAI(model="gpt-4o-mini", temperature=0),
            prompt=qual_prompt
        )

        # Quantitative scoring prompt
        score_prompt = PromptTemplate(
            input_variables=["startup_info"],
            template="""
다음 스타트업 데이터를 보고 6개 항목을 1~10점으로 매겨 JSON 형태로 반환하세요:
- Owner (30%): 창업자/팀 역량
- Opportunity (25%): 시장 기회 크기
- Product (15%): 제품/기술 우수성
- Competitive (10%): 경쟁우위
- Performance (10%): 실적/성장성
- Deal Terms (10%): 투자조건

스타트업 정보:
{startup_info}

다음 JSON 형식으로만 응답하세요:
{{"owner": 점수, "opportunity_size": 점수, "product_technology": 점수, "competitive_advantage": 점수, "performance": 점수, "deal_terms": 점수}}
"""
        )
        self.score_chain = LLMChain(
            llm=ChatOpenAI(model="gpt-4o-mini", temperature=0),
            prompt=score_prompt
        )

        # Scoring weights
        self.weights = {
            "owner": 0.30,
            "opportunity_size": 0.25,
            "product_technology": 0.15,
            "competitive_advantage": 0.10,
            "performance": 0.10,
            "deal_terms": 0.10,
        }

    def score_startup(self, startup: Startup) -> Dict[str, Any]:
        """Score a single startup and return scores with total"""
        # Validate & dump
        if isinstance(startup, dict):
            startup = Startup.model_validate(startup)
        info_json = startup.model_dump_json()

        # 1) Retrieve relevant documents
        docs = self.retriever.get_relevant_documents(startup.name)
        context = "\n\n".join([d.page_content for d in docs[:5]]) if docs else ""

        # 2) Qualitative assessment
        qa = self.qual_chain.run(company=startup.name, context=context)

        # 3) Quantitative scoring
        # score_str = self.score_chain.run(startup_info=info_json)
        print(info_json)
        score_str = self.score_chain.run(startup_info=info_json)
        print("==========================================")
        print(score_str)
        
        scores = json.loads(score_str)

        total = sum(scores[k] * self.weights[k] for k in self.weights)

        # 4) Return updated Startup
        return startup.model_copy(update={
            "scores": scores,
            "total_score": total,
            "qualitative_assessment": qa
        })

    def __call__(self, startups: List[Startup]) -> Dict[str, List[Startup]]:
        scored = [self.score_startup(s) for s in startups]
        ranked = sorted(scored, key=lambda s: s.total_score or 0, reverse=True)
        return {"ranked_startups": ranked}

# Instantiate agent
BASE = Path(__file__).resolve().parent.parent
INDEX_DIR = BASE / "vector_store" / "faiss_index"
investment_judgement_agent = InvestmentJudgmentAgent(str(INDEX_DIR))
