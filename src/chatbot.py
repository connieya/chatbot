import requests
from typing import Tuple, List
import json

class Chatbot:
    def __init__(self):
        self.vectorstore = None
        self.is_ollama_available = False
        
    def check_ollama(self, ollama_host: str = "host.docker.internal"):
        """Ollama 연결 확인"""
        try:
            ollama_url = f"http://{ollama_host}:11434"
            response = requests.get(f"{ollama_url}/api/tags", timeout=5)
            self.is_ollama_available = (response.status_code == 200)
            return self.is_ollama_available
        except:
            self.is_ollama_available = False
            return False
    
    def is_document_related_question(self, question: str, source_docs: List) -> bool:
        """질문이 문서와 관련있는지 판단"""
        # 문서 관련 키워드
        doc_keywords = [
            "ai agent", "agent", "autonomous", "semiautonomous", "snowflake",
            "document", "문서", "내용", "pdf", "파일", "기술", "정의", "정의는",
            "무엇인가", "뭐야", "what is", "definition"
        ]
        
        question_lower = question.lower()
        
        # 1. 문서 키워드가 질문에 있는지
        has_doc_keyword = any(keyword in question_lower for keyword in doc_keywords)
        
        # 2. 검색된 문서가 실제로 관련있는지 (간단한 검증)
        if source_docs:
            # 문서 내용을 하나의 문자열로 합침
            all_content = " ".join([doc.page_content.lower() for doc in source_docs])
            # 질문 단어들이 문서 내용에 있는지 확인
            question_words = set(question_lower.split())
            content_words = set(all_content.split())
            common_words = question_words.intersection(content_words)
            
            # 공통 단어가 2개 이상이면 관련 있다고 판단
            has_relevant_content = len(common_words) >= 2
        else:
            has_relevant_content = False
        
        return has_doc_keyword or has_relevant_content
    
    def ask_ollama(self, prompt: str) -> str:
        """Ollama에 직접 요청"""
        try:
            ollama_url = "http://host.docker.internal:11434"
            
            payload = {
                "model": "llama2",
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(f"{ollama_url}/api/generate", 
                                   json=payload, timeout=30)
            if response.status_code == 200:
                return response.json()["response"]
            else:
                return "Ollama 응답 생성 실패"
        except Exception as e:
            return f"Ollama 연결 오류: {str(e)}"
    
    def setup_qa_chain(self, vectorstore):
        """간단한 설정"""
        self.vectorstore = vectorstore
        self.check_ollama()
        print("✅ 챗봇 설정 완료")
    
    def ask_question(self, question: str) -> Tuple[str, List]:
        """질문에 답변 - 문서 관련성에 따라 다른 처리"""
        if not self.vectorstore:
            return "문서가 아직 처리되지 않았습니다.", []
        
        try:
            # 1. 관련 문서 검색
            source_docs = self.vectorstore.similarity_search(question, k=3)
            
            # 2. 질문이 문서와 관련있는지 판단
            is_related = self.is_document_related_question(question, source_docs)
            
            # 3. 관련성에 따라 다른 프롬프트 사용
            if is_related and source_docs:
                # 문서 관련 질문 → 문서 기반 답변
                context = "\n\n".join([doc.page_content for doc in source_docs])
                prompt = f"""다음 문서 내용을 바탕으로 질문에 답변해주세요:

문서 내용:
{context}

질문: {question}

지시사항:
- 문서에 명시된 정보를 바탕으로 답변하세요
- 문서에 없는 정보는 추가하지 마세요
- 명확하고 간결하게 답변하세요

답변:"""
                answer = self.ask_ollama(prompt) if self.is_ollama_available else "Ollama 필요"
                return answer, source_docs  # 참조 문서 표시
                
            else:
                # 일반 질문 → LLM의 일반 지식으로 답변
                prompt = f"""다음 일반 질문에 대해 당신의 지식을 바탕으로 친절하게 답변해주세요:

질문: {question}

답변:"""
                answer = self.ask_ollama(prompt) if self.is_ollama_available else "Ollama 필요"
                return answer, []  # 참조 문서 없음
            
        except Exception as e:
            return f"오류 발생: {str(e)}", []