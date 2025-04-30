# scripts/preprocess_pdf_index.py

import os
import pdfplumber
import camelot
import re
from typing import List
from sentence_transformers import SentenceTransformer
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from langchain.vectorstores import FAISS

def extract_chunks(pdf_path: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Document]:
    docs: List[Document] = []
    # 1) 텍스트 청크
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            text = re.sub(r'^\s*Page \d+\s*$', '', text, flags=re.MULTILINE)
            paras = [p.strip() for p in text.split("\n\n") if p.strip()]
            for para in paras:
                for j in range(0, len(para), chunk_size - chunk_overlap):
                    docs.append(Document(
                        page_content=para[j:j+chunk_size],
                        metadata={"page": i, "type": "text"}
                    ))
    # 2) 표 청크
    tables = camelot.read_pdf(pdf_path, pages="all", flavor="stream")
    for table in tables:
        csv = table.df.to_csv(index=False)
        docs.append(Document(
            page_content=csv,
            metadata={"page": table.page, "type": "table"}
        ))
    return docs

def build_and_save_index(
    pdf_path: str,
    index_dir: str = "faiss_index",
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
):
    # 1) 청크 추출
    docs = extract_chunks(pdf_path)

    # 2) HuggingFaceEmbeddings 래퍼 생성
    embedder = HuggingFaceEmbeddings(model_name=embedding_model)

    # 3) FAISS 색인 생성 & 저장
    os.makedirs(index_dir, exist_ok=True)
    vectorstore = FAISS.from_documents(docs, embedder)
    vectorstore.save_local(index_dir)

    print(f"🔖 FAISS index saved to `{index_dir}` (contains {len(docs)} chunks)")

if __name__ == "__main__":
    PDF_PATH = "./3. 벤처캐피탈 자율규제 우수기업(vc) 평가기준_20250204_f.pdf"
    build_and_save_index(PDF_PATH, index_dir="faiss_index")
