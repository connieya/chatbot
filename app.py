import streamlit as st
import os
import sys

# src 모듈 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.document_loader import DocumentLoader
from src.embedding_service import EmbeddingService
from src.chatbot import Chatbot

class DocumentChatbotApp:
    def __init__(self):
        self.docs_path = "/app/docs"
        self.chroma_path = "/app/chroma_db"
        self.document_loader = DocumentLoader(self.docs_path)
        self.embedding_service = EmbeddingService(self.chroma_path)
        self.chatbot = Chatbot()
        self.is_initialized = False
    
    def initialize_system(self):
        """시스템 초기화"""
        if self.is_initialized:
            return True
            
        try:
            # 문서 로드 및 처리
            st.sidebar.info("📄 문서를 로드하는 중...")
            documents = self.document_loader.load_pdf_documents()
            
            if not documents:
                st.sidebar.error("📂 docs 폴더에 PDF 파일이 없습니다.")
                return False
            
            # 문서 분할
            st.sidebar.info("✂️ 문서를 분할하는 중...")
            splits = self.document_loader.split_documents(documents)
            
            # 벡터 저장소 생성
            st.sidebar.info("🔢 임베딩 생성 중...")
            vectorstore = self.embedding_service.create_vectorstore(splits)
            
            # QA 체인 설정
            st.sidebar.info("🤖 챗봇 초기화 중...")
            self.chatbot.setup_qa_chain(vectorstore)
            
            self.is_initialized = True
            st.sidebar.success("✅ 시스템 초기화 완료!")
            return True
            
        except Exception as e:
            st.sidebar.error(f"❌ 초기화 실패: {str(e)}")
            return False

def main():
    st.set_page_config(
        page_title="다용도 AI 챗봇",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🧠 다용도 AI 챗봇")
    st.markdown("""
    **문서 분석 + 일반 대화가 가능한 AI 어시스턴트**

    ### ✨ 주요 기능
    - **📚 문서 기반 답변**: 업로드된 문서 내용을 참조하여 정확한 정보 제공
    - **💬 일반 지식 답변**: 다양한 주제에 대한 AI의 지식 활용
    - **🔍 투명한 참조**: 문서를 사용한 답변은 출처를 명확히 표시
    
    *현재 `/app/docs/` 폴더의 문서들을 학습했습니다.*
    """)
    
    # 앱 초기화
    if 'app' not in st.session_state:
        st.session_state.app = DocumentChatbotApp()
    
    app = st.session_state.app
    
    # 사이드바
    with st.sidebar:
        st.header("⚙️ 시스템 설정")
        
        if st.button("🔄 문서 재처리", help="문서를 다시 읽어서 시스템을 업데이트합니다"):
            with st.spinner("문서를 재처리하는 중..."):
                app.is_initialized = False
                if app.initialize_system():
                    st.success("문서 처리 완료!")
                else:
                    st.error("문서 처리 실패!")
        
        st.markdown("---")
        
        st.header("📁 문서 상태")
        
        # 동적 문서 정보 표시
        if os.path.exists(app.docs_path):
            docs_files = [f for f in os.listdir(app.docs_path) if f.endswith('.pdf')]
            if docs_files:
                st.success(f"📄 {len(docs_files)}개의 PDF 문서 로드됨")
                for doc_file in docs_files:
                    st.write(f"• {doc_file}")
            else:
                st.warning("📂 PDF 파일이 없습니다")
        else:
            st.error("📁 docs 폴더가 존재하지 않습니다")
        
        st.markdown("---")
        st.header("🔧 시스템 정보")
        if app.is_initialized:
            st.success("✅ 시스템 준비 완료")
        else:
            st.warning("🔄 시스템 초기화 필요")
        
        st.write("""
        - **문서 처리:** ChromaDB
        - **AI 엔진:** Ollama LLM
        - **임베딩:** HuggingFace
        """)
    
    # 자동 초기화 시도
    if not app.is_initialized:
        with st.spinner("시스템을 초기화하는 중..."):
            if app.initialize_system():
                st.success("✅ 시스템 준비 완료! 이제 질문을 시작해보세요.")
            else:
                st.error("❌ 시스템 초기화에 실패했습니다. 사이드바에서 다시 시도해주세요.")
                return
    
    # 채팅 인터페이스
    st.header("💬 대화하기")
    
    # 채팅 기록
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "안녕하세요! 🤖\n\n저는 문서 내용을 참조하거나 일반 지식으로 답변하는 AI 어시스턴트입니다.\n\n무엇이 궁금하신가요?"}
        ]
    
    # 채팅 기록 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # 질문 입력
    if prompt := st.chat_input("질문을 입력하세요..."):
        # 사용자 메시지 추가
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # AI 응답 생성
        with st.chat_message("assistant"):
            with st.spinner("답변 생성 중..."):
                answer, source_docs = app.chatbot.ask_question(prompt)
                st.markdown(answer)
                
                # 문서 관련 질문일 때만 참조 문서 표시
                if source_docs:
                    with st.expander("📎 참조 문서 보기"):
                        st.info("이 답변은 업로드된 문서 내용을 참조하여 생성되었습니다:")
                        for i, doc in enumerate(source_docs):
                            st.write(f"**문서 조각 {i+1}:**")
                            if hasattr(doc, 'metadata') and 'page' in doc.metadata:
                                st.write(f"**페이지:** {doc.metadata['page']}")
                            st.write(f"**내용:** {doc.page_content[:250]}...")
                            if i < len(source_docs) - 1:
                                st.write("---")
        
        # AI 메시지 추가
        st.session_state.messages.append({"role": "assistant", "content": answer})

if __name__ == "__main__":
    main()