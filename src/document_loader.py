import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from typing import List

class DocumentLoader:
    def __init__(self, docs_path: str = "/app/docs"):
        self.docs_path = docs_path
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100,
            length_function=len
        )
    
    def load_pdf_documents(self) -> List[Document]:
        """PDF 문서 로드"""
        documents = []
        
        # docs 폴더 내 모든 PDF 파일 처리
        for filename in os.listdir(self.docs_path):
            if filename.lower().endswith('.pdf'):
                file_path = os.path.join(self.docs_path, filename)
                try:
                    loader = PyPDFLoader(file_path)
                    loaded_docs = loader.load()
                    documents.extend(loaded_docs)
                    print(f"✅ {filename} 로드 완료 ({len(loaded_docs)} 페이지)")
                except Exception as e:
                    print(f"❌ {filename} 처리 중 오류: {str(e)}")
        
        return documents
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """문서를 청크로 분할"""
        if not documents:
            return []
        
        splits = self.text_splitter.split_documents(documents)
        print(f"📄 문서를 {len(splits)}개의 청크로 분할했습니다.")
        return splits