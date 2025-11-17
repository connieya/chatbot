# AI 문서 챗봇

문서 기반 질의응답과 일반 대화가 가능한 RAG(Retrieval-Augmented Generation) 기반 AI 챗봇입니다.

---
![alt text](image.png)

## 목차

- [개발 언어 및 선택 이유](#개발-언어-및-선택-이유)
- [사용한 LLM 모델 및 선택 이유](#사용한-llm-모델-및-선택-이유)
- [프로그램 실행 방법](#프로그램-실행-방법)
- [프로젝트 구조](#프로젝트-구조)
- [기술 스택](#기술-스택)
- [현재 한계](#현재-한계)
- [향후 개선 방향](#향후-개선-방향)

---

## 개발 언어 및 선택 이유

### 개발 언어: **Python**

### 선택 이유

1. **풍부한 AI/ML 생태계**

   - LangChain, HuggingFace, PyTorch 등 AI 라이브러리 지원
   - RAG 구현에 필요한 도구들이 Python 중심

2. **빠른 프로토타이핑**

   - 간결한 문법으로 개발 속도 향상
   - Streamlit으로 웹 UI를 빠르게 구축 가능

3. **활발한 커뮤니티**

   - AI/ML 분야에서 가장 널리 사용되는 언어
   - 문제 해결을 위한 자료와 예제가 풍부

4. **라이브러리 호환성**
   - LangChain, ChromaDB, HuggingFace 등 주요 라이브러리가 Python 네이티브
   - 패키지 관리가 용이 (pip, conda)

---

## 사용한 LLM 모델 및 선택 이유

### LLM 모델: **Ollama (mistral)**

### 선택 이유

1. **로컬 실행 가능**

   - API 키 없이 로컬에서 실행
   - 데이터 프라이버시 보호
   - 인터넷 연결 없이도 동작

2. **비용 효율성**

   - OpenAI API 등 유료 서비스 대비 비용 절감
   - 사용량 제한 없음

3. **다국어 지원**

   - mistral 모델의 우수한 한국어 처리 능력
   - 영어와 한국어 모두 자연스러운 답변 생성

4. **커스터마이징 가능**

   - 다양한 오픈소스 모델 지원 (llama2, mistral, codellama 등)
   - 모델 교체가 쉬움

5. **Docker 환경과의 호환성**
   - 컨테이너 환경에서 쉽게 연동
   - `host.docker.internal`을 통한 네트워크 연결

### 임베딩 모델: **HuggingFace (paraphrase-multilingual-MiniLM-L12-v2)**

### 선택 이유

1. **다국어 지원**

   - 한국어와 영어 모두 지원
   - 한국어 문서 처리에 적합

2. **경량 모델**

   - 작은 모델 크기로 빠른 처리 속도
   - CPU 환경에서도 효율적

3. **오픈소스**
   - 무료 사용 가능
   - 로컬에서 실행 가능

---

## 프로그램 실행 방법

### 사전 요구사항

1. **Python 3.9, 3.10, 3.11, 3.12**

   - 3.13, 3.14 버전은 호환성 문제가 있을 수 있습니다
   - Docker 사용시 Python 버전 문제 없음

2. **Ollama 설치 및 실행**

#### 운영체제별 설치

```bash
# macOS
brew install ollama

# Windows
# 1. https://ollama.ai/download에서 설치
# 2. 또는: winget install Ollama.Ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh
```

#### Ollama 모델 다운로드

```bash
# mistral 모델 다운로드 (권장 - 한국어 성능 우수)
ollama pull mistral

# 또는 대체 모델
ollama pull llama2
ollama pull gemma:7b
```

#### Ollama 실행

```bash
# Ollama 서버 실행 (별도 터미널에서)
ollama serve
```

### 설치 및 실행

1. **저장소 클론**

   ```bash
   git clone <repository-url>
   cd chatbot
   ```

2. **가상환경 생성 및 활성화**

   ```bash
   python -m venv .venv

   # macOS/Linux
   source .venv/bin/activate

   # Windows
   .venv\Scripts\activate
   ```

3. **의존성 패키지 설치**

   ```bash
   pip install -r requirements.txt
   ```

4. **환경 변수 설정 (선택사항)**

   ```bash
   # .env 파일 생성
   echo "OLLAMA_HOST=host.docker.internal" > .env
   ```

5. **문서 준비**

   ```bash
   # docs 폴더에 PDF 파일 배치
   mkdir -p docs
   cp your_document.pdf docs/
   ```

6. **Streamlit 앱 실행**

   ```bash
   streamlit run app.py
   ```

7. **브라우저에서 접속**
   - 자동으로 브라우저가 열리거나
   - 터미널에 표시된 URL로 접속 (일반적으로 `http://localhost:8501`)

### Docker를 사용한 실행 (선택사항)

```bash
# Docker 이미지 빌드
docker build -t chatbot .

# Docker 컨테이너 실행
docker run -p 8501:8501 chatbot
```

---

## 프로젝트 구조

```
chatbot/
├── app.py                 # Streamlit 메인 애플리케이션
├── src/
│   ├── chatbot.py        # 챗봇 로직 (Ollama 연동)
│   ├── document_loader.py # PDF 문서 로더
│   └── embedding_service.py # 임베딩 및 벡터 DB 관리
├── docs/                 # PDF 문서 저장 폴더
├── chroma_db/           # ChromaDB 벡터 저장소 (자동 생성)
├── requirements.txt     # Python 패키지 의존성
└── README.md           # 프로젝트 문서
```

---

## 기술 스택

- **프레임워크**: Streamlit
- **RAG 프레임워크**: LangChain
- **벡터 데이터베이스**: ChromaDB
- **LLM**: Ollama (mistral)
- **임베딩**: HuggingFace Transformers
- **문서 처리**: PyPDF

---

## 현재 한계

1. **문서 의존적 키워드 하드코딩**

   - 새로운 PDF 추가 시 키워드 분석과 코드 수동 수정 필요
   - 문서 변경마다 재배포가 필요해 민첩성이 떨어짐
   - 다양한 주제를 가진 문서를 동시에 지원하기 어려움

2. **질문 분류 정확성 한계**

   - 키워드 매칭 기반 분류로 오탐지/미탐지가 발생할 수 있음
   - 복합적·맥락적인 질문을 정확히 분류하기 어려움
   - 문서와 무관하지만 키워드가 포함된 질문도 문서 관련으로 오인식 가능

3. **단일 문서 지원 구조**

   - 한 번에 하나의 PDF만 처리하며 다중 문서 통합 검색 미지원
   - 문서 간 크로스 레퍼런싱이나 연관 문서 추천이 불가능
   - 문서별 가중치/우선순위 관리 기능이 없음

4. **확장성 및 운영 한계**

   - 도메인 특화 지식이 필요할 경우 매번 추가 설정 필요
   - 다국어 문서 처리 지원이 제한적
   - 성능 모니터링·로깅 체계가 없어 운영 상태 파악이 어려움

5. **VectorDB 검색 효율성**
   - 모든 질문에 대해 VectorDB를 조회해 리소스가 낭비될 수 있음
   - 무의미한 검색 결과를 필터링하는 후처리 로직이 부족
   - 유사도 임계값을 상황에 맞게 조정하는 기능이 미구현

---

## 향후 개선 방향

1. **동적 키워드 추출 시스템**

   ```python
   def extract_document_keywords(documents: List[Document]) -> List[str]:
       """문서 초기화 시 자동 키워드 추출"""
   ```

   - 문서 초기화 시 자동으로 핵심 키워드를 추출하여 수동 작업 제거
   - 새로운 문서가 추가되어도 별도 배포 없이 즉시 반영 가능

2. **LLM 기반 질문 분류기**

   - 질문 의도 파악을 LLM에게 위임해 오탐/미탐 최소화
   - 컨텍스트 인식 분류 및 복합 질문 처리 능력 향상
   - 도메인 특화 분류 규칙을 학습시켜 다양성 확보

3. **다중 문서 관리 아키텍처**

   ```python
   class MultiDocumentManager:
       def __init__(self):
           self.documents = {}  # 문서별 메타데이터 및 벡터스토어 관리
           self.cross_reference = CrossReferenceEngine()
   ```

   - 문서별 네임스페이스 관리, 통합 검색, 연관 문서 추천 제공
   - 문서 간 크로스 레퍼런싱과 가중치 기반 검색 우선순위 지원

4. **지능형 검색 최적화**

   ```python
   def smart_retrieval(question: str) -> Tuple[List[Document], bool]:
       """질문 분석을 통한 검색 최적화"""
       # 1. 질문 의도 분석
       # 2. 필요 시에만 VectorDB 검색 수행
       # 3. 검색 결과 품질 평가 및 필터링
   ```

   - 불필요한 검색을 줄여 응답 시간을 단축하고 리소스 사용 효율화
   - 검색 결과 품질을 평가해 의미 없는 문서 컨텍스트를 제거

5. **자동화 운영 파이프라인**

   - 새 문서 업로드 시 키워드 추출부터 시스템 재초기화까지 자동 처리
   - 문서 변경 감지를 통한 증분 업데이트 지원
   - 성능 모니터링 대시보드 및 알림 시스템 구축

6. **고급 RAG 기능**
   - 하이브리드 검색(키워드 + 벡터) 전략 도입
   - 질문 리라이트/확장으로 검색 적합성 향상
   - 소스 신뢰도 평가 및 가중치 부여, 대화 세션 컨텍스트 유지

---
