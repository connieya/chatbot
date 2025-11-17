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
        """질문이 문서와 관련있는지 판단 - 개선된 키워드"""
        question_lower = question.lower()
        
        # 문서 특정 주제 (목차 기반으로 확장)
        document_specific_topics = [
            # 문서 메타데이터
            "market sharing", "erica yu", "ai agent market",
            
            # 1. Definition about AI Agent
            "definition", "gartner definition", "autonomous", "semiautonomous",
            "software entities", "perceive", "make decisions", "take actions", 
            "achieve goals", "digital environments", "physical environments",
            
            # 2. Growing Market momentum
            "growing market", "market momentum", "andrew ng", "snowflake build 2024",
            "investment boom", "funding", "startups", "market potential",
            "enterprise software", "agentic ai", "autonomously", 
            "market growth", "cb insights", "organizations",
            
            # 3. About Manus
            "manus", "breakthrough", "hype",
            
            # 4. Technological readiness
            "technological readiness", "boost",
            
            # 5. Future trends
            "future trends", "independent agency", "multiagent systems", "mas",
            "improvement", "capabilities",
            
            # 6. Landscape of AI Agent
            "landscape", "big tech", "general ai agent", "specialized agents",
            "capital markets", "private ai agent", "infrastructure", "framework",
            "tooling", "alibaba cloud", "development platforms", "ecosystem",
            
            # 7. Customer list
            "customer list",
            
            # 핵심 숫자 및 통계
            "33%", "15%", "5.1 billion", "47.1 billion", "2030", "2024",
            "63%", "4x", "3x", "15k", "q4 2024",
            
            # 한국어 키워드
            "시장 점유율", "에리카 유", "정의", "자율", "반자율",
            "시장 성장", "투자 붐", "스타트업", "기업용 소프트웨어",
            "미래 동향", "다중 에이전트", "랜드스케이프", "인프라",
            "고객 목록", "알리바바 클라우드"
        ]
        
        has_topic_keyword = any(topic in question_lower for topic in document_specific_topics)
        
        # 더 다양한 질문 패턴 인식
        question_patterns = [
            "정의", "정의는", "무엇인가", "뭐야", "what is", "definition",
            "특징", "특성", "feature", "characteristic", 
            "기능", "function", "역할", "role",
            "종류", "type", "유형", "category",
            "활용", "application", "사용", "use",
            "전망", "예측", "forecast", "prediction",
            "현황", "상황", "status", "current state",
            "규모", "크기", "size", "scale",
            "성장", "성장률", "growth", "rate",
            "동향", "트렌드", "trend", "tendency",
            "비율", "퍼센트", "percent", "percentage"
        ]
        
        has_question_pattern = any(pattern in question_lower for pattern in question_patterns)
        
        # 주제 키워드가 있고, 질문 패턴이 있거나 문장이 충분히 길 때
        return has_topic_keyword and (has_question_pattern or len(question.split()) >= 3)
        
    def ask_ollama(self, prompt: str, is_korean_question: bool = False) -> str:
        """Ollama에 직접 요청 - mistral 모델 사용"""
        try:
            ollama_url = "http://host.docker.internal:11434"
            
            # 한국어 질문일 경우 프롬프트 강화
            if is_korean_question:
                enhanced_prompt = f"""다음 질문이나 지시에 대해 한국어로 친절하게 답변해주세요:

                {prompt}

                지시사항:
                - 반드시 한국어로 답변해주세요
                - 명확하고 간결하게 답변해주세요
                - 자연스러운 한국어 문장을 사용해주세요

                답변:"""
            else:
                enhanced_prompt = prompt
            
            payload = {
                "model": "mistral",  # llama2 → mistral로 변경
                "prompt": enhanced_prompt,
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
        print("✅ 챗봇 설정 완료 (mistral 모델)")
    
    def is_korean_question(self, question: str) -> bool:
        """질문이 한국어인지 판단"""
        korean_chars = set('가나다라마바사아자차카타파하햐여요우유으이')
        return any(char in korean_chars for char in question)
    
    def ask_question(self, question: str) -> Tuple[str, List]:
        """질문에 답변 - 문서 관련성에 따라 다른 처리"""
        if not self.vectorstore:
            return "문서가 아직 처리되지 않았습니다.", []
        
        try:
            # 1. 관련 문서 검색
            source_docs = self.vectorstore.similarity_search(question, k=3)
            
            # 2. 질문이 문서와 관련있는지 판단
            is_related = self.is_document_related_question(question, source_docs)
            
            # 3. 한국어 질문인지 확인
            is_korean = self.is_korean_question(question)
            
            # 4. 관련성에 따라 다른 프롬프트 사용
            if is_related and source_docs:
                # 문서 관련 질문 → 문서 기반 답변
                context = "\n\n".join([doc.page_content for doc in source_docs])
                prompt = f"""You are a helpful AI assistant. Provide accurate answers based on the provided document content.

                Document content:
                {context}

                Question: {question}

                Instructions:
                - Answer based on document content when relevant
                - Provide clear and concise answers
                - Respond in the same language as the question

                Answer:"""
                answer = self.ask_ollama(prompt, is_korean) if self.is_ollama_available else "Ollama 필요"
                return answer, source_docs  # 참조 문서 표시
                
            else:
                # 일반 질문 → LLM의 일반 지식으로 답변
                if is_korean:
                    prompt = f"""다음 일반 질문에 대해 한국어로 친절하게 답변해주세요:

                    질문: {question}

                    지시사항:
                    - 반드시 한국어로 답변해주세요
                    - 명확하고 간결하게 설명해주세요
                    - 자연스러운 한국어 문장을 사용해주세요

                    답변:"""
                else:
                    prompt = f"""Please answer the following general question based on your knowledge:

                    Question: {question}

                    Instructions:
                    - Provide a clear and helpful answer
                    - Be concise and accurate

                    Answer:"""
                
                answer = self.ask_ollama(prompt, is_korean) if self.is_ollama_available else "Ollama 필요"
                return answer, []  # 참조 문서 없음
            
        except Exception as e:
            return f"오류 발생: {str(e)}", []