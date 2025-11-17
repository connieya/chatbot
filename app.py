import streamlit as st
import os
import sys
from pathlib import Path

# src 모듈 경로 추가 (더 안전한 방법)
current_dir = Path(__file__).parent
src_path = current_dir / "src"
sys.path.append(str(src_path))

from src.document_loader import DocumentLoader
from src.embedding_service import EmbeddingService
from src.chatbot import Chatbot

class AppConfig:
    """애플리케이션 설정"""
    DOCS_PATH = "/app/docs"
    CHROMA_PATH = "/app/chroma_db"

class DocumentChatbotApp:
    def __init__(self):
        self.config = AppConfig()
        self.document_loader = DocumentLoader(self.config.DOCS_PATH)아
        self.embedding_service = EmbeddingService(self.config.CHROMA_PATH)
        self.chatbot = Chatbot()
        self.is_initialized = False
    
    def _render_sidebar(self):
        """사이드바 렌더링"""
        with st.sidebar:
            self._render_system_settings()
            self._render_document_status()
            self._render_system_info()
    
    def _render_system_settings(self):
        """시스템 설정 섹션"""
        st.header("⚙️ 시스템 설정")
        if st.button("🔄 문서 재처리", help="문서를 다시 읽어서 시스템을 업데이트합니다"):
            self._reprocess_documents()
    
    def _reprocess_documents(self):
        """문서 재처리"""
        with st.spinner("문서를 재처리하는 중..."):
            self.is_initialized = False
            if self.initialize_system():
                st.success("문서 처리 완료!")
            else:
                st.error("문서 처리 실패!")
    
    def _render_document_status(self):
        """문서 상태 섹션"""
        st.header("📁 문서 상태")
        docs_path = Path(self.config.DOCS_PATH)
        
        if docs_path.exists():
            pdf_files = list(docs_path.glob("*.pdf"))
            if pdf_files:
                st.success(f"📄 {len(pdf_files)}개의 PDF 문서 로드됨")
                for pdf_file in pdf_files:
                    st.write(f"• {pdf_file.name}")
            else:
                st.warning("📂 PDF 파일이 없습니다")
        else:
            st.error("📁 docs 폴더가 존재하지 않습니다")
        
        st.markdown("---")
    
    def _render_system_info(self):
        """시스템 정보 섹션"""
        st.header("🔧 시스템 정보")
        if self.is_initialized:
            st.success("✅ 시스템 준비 완료")
        else:
            st.warning("🔄 시스템 초기화 필요")
        
        st.write("""
        - **문서 처리:** ChromaDB
        - **AI 엔진:** Ollama LLM
        - **임베딩:** HuggingFace
        """)
    
    def initialize_system(self):
        """시스템 초기화"""
        if self.is_initialized:
            return True
            
        try:
            steps = [
                ("📄 문서를 로드하는 중...", self.document_loader.load_pdf_documents),
                ("✂️ 문서를 분할하는 중...", None),  # 분할은 별도 처리
                ("🔢 임베딩 생성 중...", None),
                ("🤖 챗봇 초기화 중...", None)
            ]
            
            # 문서 로드
            st.sidebar.info(steps[0][0])
            documents = steps[0][1]()
            
            if not documents:
                st.sidebar.error("📂 docs 폴더에 PDF 파일이 없습니다.")
                return False
            
            # 문서 분할
            st.sidebar.info(steps[1][0])
            splits = self.document_loader.split_documents(documents)
            
            # 임베딩 생성
            st.sidebar.info(steps[2][0])
            vectorstore = self.embedding_service.create_vectorstore(splits)
            
            # 챗봇 초기화
            st.sidebar.info(steps[3][0])
            self.chatbot.setup_qa_chain(vectorstore)
            
            self.is_initialized = True
            st.sidebar.success("✅ 시스템 초기화 완료!")
            return True
            
        except Exception as e:
            st.sidebar.error(f"❌ 초기화 실패: {str(e)}")
            return False

def render_chat_interface(app):
    """채팅 인터페이스 렌더링"""
    st.header("💬 대화하기")
    
    # 채팅 기록 초기화
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
        process_user_input(app, prompt)

def process_user_input(app, prompt):
    """사용자 입력 처리"""
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # AI 응답 생성
    with st.chat_message("assistant"):
        with st.spinner("답변 생성 중..."):
            answer, source_docs = app.chatbot.ask_question(prompt)
            st.markdown(answer)
            
            # 참조 문서 표시
            if source_docs:
                render_source_documents(source_docs)
    
    # AI 메시지 추가
    st.session_state.messages.append({"role": "assistant", "content": answer})

def render_source_documents(source_docs):
    """참조 문서 렌더링"""
    with st.expander("📎 참조 문서 보기"):
        st.info("이 답변은 업로드된 문서 내용을 참조하여 생성되었습니다:")
        for i, doc in enumerate(source_docs):
            st.write(f"**문서 조각 {i+1}:**")
            if hasattr(doc, 'metadata') and 'page' in doc.metadata:
                st.write(f"**페이지:** {doc.metadata['page']}")
            st.write(f"**내용:** {doc.page_content[:250]}...")
            if i < len(source_docs) - 1:
                st.write("---")

def main():
    # 페이지 설정
    st.set_page_config(
        page_title="다용도 AI 챗봇",
        page_icon="🤖",
        layout="wide"
    )
    
    # 헤더
    st.title("🧠 다용도 AI 챗봇")
    st.markdown("""
    **문서 분석 + 일반 대화가 가능한 AI 어시스턴트**
    """)
    
    # 앱 초기화
    if 'app' not in st.session_state:
        st.session_state.app = DocumentChatbotApp()
    
    app = st.session_state.app
    
    # 사이드바 렌더링
    app._render_sidebar()
    
    # 시스템 초기화
    if not app.is_initialized:
        with st.spinner("시스템을 초기화하는 중..."):
            if app.initialize_system():
                st.success("✅ 시스템 준비 완료! 이제 질문을 시작해보세요.")
            else:
                st.error("❌ 시스템 초기화에 실패했습니다. 사이드바에서 다시 시도해주세요.")
                return
    
    # 채팅 인터페이스
    render_chat_interface(app)

if __name__ == "__main__":
    main()