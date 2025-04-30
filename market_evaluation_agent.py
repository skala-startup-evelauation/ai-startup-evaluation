from typing import List, Optional
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.docstore.document import Document
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import re
from dotenv import load_dotenv
load_dotenv()

class AIResearchAgent:
    def __init__(self):
        # API 키를 환경 변수에서 로드
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        os.environ["OPENAI_API_KEY"] = self.openai_api_key
        
        # 설정값 환경 변수에서 로드
        self.chunk_size = int(os.getenv("CHUNK_SIZE", "512"))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "100"))
        self.model_name = os.getenv("MODEL_NAME", "gpt-4")
        self.temperature = float(os.getenv("TEMPERATURE", "0"))
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        
        self.llm = ChatOpenAI(model_name="gpt-4", temperature=0)
        self.embedding = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
        
        # 프롬프트 템플릿 설정
        self.summary_template = """아래 제목과 내용을 참고해서 핵심 내용을 요약해줘. 3~4문장으로 작성해줘.

[제목] {title}
[내용]
{content}"""
        
        self.summary_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                template=self.summary_template,
                input_variables=["title", "content"]
            )
        )

    def process_documents(self, 
                         base_path: str,
                         pdf_files: dict,
                         persist_dir: str) -> None:
        """문서 처리 및 벡터 DB 저장"""
        all_docs = []
        
        # 문서 처리
        for key, (filename, page_list) in pdf_files.items():
            print(f"📘 {key} 처리 중...")
            path = os.path.join(base_path, filename)
            loader = PyMuPDFLoader(path)
            docs = loader.load()
            
            # page_list가 None인 경우 모든 페이지 사용
            if page_list is None:
                target_pages = docs
            else:
                target_pages = [d for d in docs if d.metadata["page"] in page_list]
            
            for doc in target_pages:
                sections = self._extract_sections(doc, key)
                all_docs.extend(sections)
        
        # 청킹 및 벡터 DB 저장
        splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=100)
        split_docs = splitter.split_documents(all_docs)
        
        vectordb = Chroma.from_documents(
            documents=split_docs,
            embedding=self.embedding,
            persist_directory=persist_dir
        )
        vectordb.persist()
        print(f"✅ 완료: 문서 {len(split_docs)}개 저장됨")
        
        # QA 시스템 초기화
        self._initialize_qa_system(persist_dir)

    def _extract_sections(self, doc: Document, file_key: str) -> List[Document]:
        """섹션 추출 및 요약"""
        text = doc.page_content
        sections = []
        
        # 문서 유형별 구분
        if file_key == "IF_Strategy":
            split_sections = re.split(r"(<[^<>]{2,40}>)", text)
        elif file_key == "StartupRecipe":
            split_sections = [text]
        elif file_key == "RE169":
            split_sections = re.split(r"(\[표\s?\d{1,2}-\d{1,2}\]|\[그림\s?\d{1,2}-\d{1,2}\])", text)
        else:
            split_sections = [text]
            
        # 섹션 처리
        for i in range(0, len(split_sections), 2):
            title = split_sections[i].strip()
            content = split_sections[i + 1].strip() if i + 1 < len(split_sections) else ""
            
            if len(content) < 30:
                continue
                
            try:
                summary = self.summary_chain.run(title=title, content=content)
                full_text = f"[제목] {title}\n\n[내용]\n{content}\n\n[GPT 설명]\n{summary}"
                sections.append(Document(page_content=full_text, metadata=doc.metadata))
            except Exception as e:
                print(f"❌ GPT 오류 (page {doc.metadata['page']+1}): {e}")
                
        return sections

    def _initialize_qa_system(self, persist_dir: str) -> None:
        """QA 시스템 초기화"""
        vectordb = Chroma(
            persist_directory=persist_dir,
            embedding_function=self.embedding
        )
        
        # Retriever 설정
        base_retriever = vectordb.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": 8,
                "fetch_k": 20,
                "lambda_mult": 0.7
            }
        )
        
        # Multi-Query Retriever
        self.retriever = MultiQueryRetriever.from_llm(
            retriever=base_retriever,
            llm=self.llm
        )
        
        # QA 체인
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=self.retriever,
            return_source_documents=True
        )

    def ask(self, question: str) -> str:
        """질문에 답변"""
        try:
            result = self.qa_chain.invoke(question)
            return result["result"]
        except Exception as e:
            return f"❌ 오류 발생: {str(e)}"

# 사용 예시
if __name__ == "__main__":
    # 에이전트 초기화
    agent = AIResearchAgent()
    
    # 문서 처리
    base_path = "C:/Users/lsm22/Desktop/skala/0430startup"
    pdf_files = {
     "RE169": ("RE169_국내AI창업기업_비즈니스_현황분석.pdf", list(range(19, 43)) + list(range(83, 95))),  # 3장(20~43p), 5장(84~95p)
        "IF_Strategy": ("IF_Strategy24-03_글로벌_정부·민간_분야_AI_투자_동향_분석_최종.pdf", list(range(10, 1000))),  # 11페이지부터 끝까지 (참고문헌 제외는 후처리에서)
        "StartupRecipe": ("250130__startup-recipe_investment-report_24_v001.pdf", None)  # 전체 페이지
    }
    persist_dir = "C:/Users/lsm22/Desktop/skala/0430startup/vector_db_scenario_test"
    
    # 문서 처리 및 DB 저장
    agent.process_documents(base_path, pdf_files, persist_dir)
    
    # 질문 테스트
    questions = [
        "최근 투자 규모나 성장률이 높은 AI 분야는?",
        "투자 상위 분야 중 전반적인 특징이 뭔가요?",
        "이 분야에서 활동 중인 AI 기업들은 무슨 일을 하나요?"
    ]
    
    for q in questions:
        print(f"\n🧾 질문: {q}")
        answer = agent.ask(q)
        print(f"💡 답변:\n{answer}")