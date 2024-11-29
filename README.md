# Korean Resume Optimizer

이력서 최적화 도구는 지원하고자 하는 회사에 맞춰 이력서를 자동으로 최적화해주는 웹 애플리케이션입니다.

## 기능 설명

- 실시간 회사 정보 분석
- 회사 문화와 가치관 파악
- 이력서 맞춤형 최적화
- 웹 기반 사용자 인터페이스
- 한국어 지원

## 시작하기

### 1. 사전 요구사항

- Python 3.x
- Ollama 설치됨
- Gemma2 모델 설치됨

### 2. Ollama 설정

```bash
# Ollama가 설치되어 있지 않다면 설치
curl https://ollama.ai/install.sh | sh

# Gemma2 모델 다운로드
ollama pull gemma2:latest
```

### 3. 프로젝트 설정

```bash
# 1. 가상환경 생성
python3 -m venv venv

# 2. 가상환경 활성화
# macOS/Linux:
source venv/bin/activate
# Windows:
# .\venv\Scripts\activate

# 3. 필요한 패키지 설치
pip install -r requirements.txt
```

### 4. 애플리케이션 실행

```bash
# 1. Ollama 서버 시작 (새 터미널에서)
ollama serve

# 2. 애플리케이션 실행 (다른 터미널에서)
python app.py
```

이제 브라우저에서 http://localhost:5000 에 접속하여 사용할 수 있습니다.

## 사용 방법

1. 웹 브라우저에서 http://localhost:5000 접속
2. 지원하고자 하는 회사명 입력
3. 현재 이력서 내용 입력
4. "이력서 최적화하기" 버튼 클릭
5. 최적화된 이력서와 회사 분석 결과 확인

## 주요 특징

- 실시간 회사 정보 수집
- AI 기반 이력서 최적화
- 회사의 가치관과 문화 분석
- 정확성 유지
- 성과 중심적 서술 변환

## 기술 스택

- Python/Flask
- Ollama (Gemma2 모델)
- HTML/JavaScript
- BeautifulSoup4 (웹 스크래핑)
- Google Search API

## 문제 해결

문제가 발생하면 다음을 확인해주세요:

1. Ollama가 실행 중인지 확인
```bash
curl http://localhost:11434/api/tags
```

2. Gemma2 모델이 설치되어 있는지 확인
```bash
ollama list
```

3. 가상환경이 활성화되어 있는지 확인
```bash
# 터미널 프롬프트에 (venv)가 표시되어 있어야 함
```
