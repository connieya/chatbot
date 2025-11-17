import os
from typing import List

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document


class EmbeddingService:
    def __init__(self, persist_directory: str = "/app/chroma_db"):
        self.persist_directory = persist_directory
        self.embedding_model = None
        self.vectorstore = None
        
    def initialize_embedding_model(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        """임베딩 모델 초기화"""
        self.embedding_model = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        print(f"✅ 임베딩 모델 로드 완료: {model_name}")
    
    def create_vectorstore(self, documents: List[Document]) -> Chroma:
        """벡터 저장소 생성 (기존 데이터 있으면 재사용)"""
        
        # 기존 VectorDB 확인
        if os.path.exists(self.persist_directory) and os.listdir(self.persist_directory):
            print("✅ 기존 VectorDB 발견, 재사용")
            return self.load_existing_vectorstore()
        else:
            print("🆕 새 VectorDB 생성")
            self.vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embedding_model,
                persist_directory=self.persist_directory
            )
            return self.vectorstore
    
    def load_existing_vectorstore(self) -> Chroma:
        """기존 벡터 저장소 로드"""
        if not self.embedding_model:
            self.initialize_embedding_model()
        
        self.vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embedding_model
        )
        print("✅ 기존 벡터 저장소 로드 완료")
        return self.vectorstore
