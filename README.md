# AI 발표 코치

발표 주제와 발표 대본을 입력하면 AI가 발표 구조, 전달력, 예상 질문, 수정 대본, 발표 전 체크리스트를 생성해주는 웹 기반 AI 발표 코칭 서비스입니다.

기존 Streamlit 기반 `ai-presentation-coach` 아이디어를 이번 미션 요구사항에 맞게 **순수 HTML/CSS/JavaScript 프론트엔드 + Vercel Python Serverless Function 백엔드** 구조로 재구성했습니다.

---

## 1. 서비스 개요

### 서비스명

AI 발표 코치

### 서비스 목적

대학생이나 발표 준비자가 발표 대본의 구조와 전달력을 스스로 점검하기 어려운 문제를 해결하기 위해 만들었습니다.  
사용자가 발표 주제와 대본을 입력하면 AI가 발표 구조, 전달력, 개선점, 예상 질문을 분석해 발표 준비를 도와줍니다.

### 타겟 사용자

- 대학 수업 발표를 준비하는 학생
- 팀 프로젝트 발표를 준비하는 사용자
- 졸업 프로젝트 또는 공모전 발표를 준비하는 사용자
- 발표 대본의 흐름과 예상 질문을 미리 점검하고 싶은 사용자

---

## 2. 배포 URL

Vercel 배포 후 아래 주소를 실제 배포 URL로 수정합니다.

```text
https://your-vercel-project-url.vercel.app
```

---

## 3. 기술 스택

| 영역 | 기술 |
|---|---|
| 프론트엔드 | HTML, CSS, JavaScript |
| 백엔드 | Vercel Serverless Functions - Python |
| AI API | Gemini API |
| 배포 | Vercel |
| 버전 관리 | Git / GitHub |

---

## 4. 프로젝트 구조

```text
ai-presentation-coach/
├── index.html
├── css/
│   └── style.css
├── js/
│   └── main.js
├── api/
│   └── analyze.py
├── docs/
│   ├── service_plan.md
│   └── ai_coding_evidence.md
├── screenshots/
│   └── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── .python-version
└── README.md
```

---

## 5. 페이지 / 섹션 구성

본 서비스는 하나의 웹페이지 안에 최소 3개 이상의 섹션을 제공합니다.

| 섹션 | 설명 |
|---|---|
| 홈 | 서비스 핵심 소개와 분석 시작 버튼 |
| 서비스 소개 | 타겟 사용자와 서비스 가치 설명 |
| AI 발표 분석 | 발표 주제와 대본 입력 후 AI 분석 결과 출력 |
| 사용 방법 | 서비스 사용 절차 안내 |
| FAQ | API 키, 응답 지연, 결과 신뢰도 등 안내 |

상단 메뉴를 통해 각 섹션으로 이동할 수 있습니다.

---

## 6. 핵심 AI 기능

### 입력

- 발표 주제
- 발표 유형
- 목표 발표 시간
- 발표 대본

### 출력

- 예상 발표 시간
- 발표 점수
- 도입/본론/결론 구조 분석
- 장점
- 개선점
- 수정 발표 대본
- 예상 질문과 답변
- 발표 전 체크리스트
- 핵심 조언 한 문장

---

## 7. AI 기능 흐름

```text
사용자 입력
→ JavaScript에서 fetch('/api/analyze') 요청
→ api/analyze.py에서 Gemini API 호출
→ 분석 결과 JSON 반환
→ JavaScript가 결과를 화면에 렌더링
```

프론트엔드의 `js/main.js`는 사용자가 입력한 내용을 JSON으로 만들어 `/api/analyze`에 POST 요청을 보냅니다.

```javascript
fetch("/api/analyze", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify(payload)
});
```

---

## 8. 실패 처리 기준

| 상황 | 처리 방식 |
|---|---|
| 발표 주제 또는 대본이 비어 있음 | “발표 주제와 발표 대본을 모두 입력해주세요.” 메시지 출력 |
| 발표 대본이 너무 짧음 | “발표 대본은 최소 50자 이상 입력해주세요.” 메시지 출력 |
| API 응답 지연 | 일정 시간 후 “AI 응답이 지연되고 있습니다.” 메시지 출력 |
| API 오류 | 기본 분석 결과 또는 오류 안내 메시지 출력 |
| JSON 형식 오류 | 서버에서 잘못된 요청 형식 안내 |

API 키가 없거나 AI API 호출에 실패하더라도 서비스가 완전히 중단되지 않도록 기본 분석 결과를 반환하는 fallback 로직을 포함했습니다.

---

## 9. 환경 변수 설정

API 키는 코드에 직접 작성하지 않고 환경 변수로 관리합니다.

`.env.example` 파일 예시:

```text
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

실제 키가 들어간 `.env` 파일은 GitHub에 올리지 않습니다.

Vercel 프로젝트 설정에서는 다음 환경 변수를 추가합니다.

| 이름 | 값 |
|---|---|
| `GEMINI_API_KEY` | 본인의 Gemini API 키 |
| `GEMINI_MODEL` | `gemini-2.5-flash` |

---

## 10. 로컬 실행 방법

### 1) 저장소 복제

```bash
git clone https://github.com/choalbin010201/ai-presentation-coach.git
```

### 2) 프로젝트 폴더 이동

```bash
cd ai-presentation-coach
```

### 3) 패키지 설치

```bash
pip install -r requirements.txt
```

### 4) Vercel CLI로 로컬 실행

```bash
vercel dev
```

브라우저에서 아래 주소로 접속합니다.

```text
http://localhost:3000
```

---

## 11. 배포 방법

1. GitHub 저장소에 프로젝트 코드를 push합니다.
2. Vercel에 로그인합니다.
3. Vercel에서 GitHub 저장소를 Import합니다.
4. Environment Variables에 `GEMINI_API_KEY`를 추가합니다.
5. Deploy를 실행합니다.
6. 배포된 URL에서 메뉴 이동, 반응형 화면, AI 분석 기능을 테스트합니다.

---

## 12. 반응형 확인

본 서비스는 CSS media query를 사용해 모바일 화면에서도 레이아웃이 깨지지 않도록 구현했습니다.

확인할 화면 크기 예시:

- 데스크톱: 1440px 또는 1280px
- 모바일: 390px 또는 430px

---

## 13. 제출용 스크린샷

`screenshots/` 폴더에 다음 스크린샷을 저장합니다.

```text
screenshots/
├── desktop_home.png
├── mobile_home.png
├── ai_input.png
├── ai_result.png
├── ai_error.png
└── ai_coding_process.png
```

README에 첨부할 예시는 다음과 같습니다.

![데스크톱 홈 화면](./screenshots/desktop_home.png)
![모바일 화면](./screenshots/mobile_home.png)
![AI 입력 화면](./screenshots/ai_input.png)
![AI 분석 결과](./screenshots/ai_result.png)
![AI 코딩 도구 사용 과정](./screenshots/ai_coding_process.png)

---

## 14. 서비스 기획서

서비스 기획서는 `docs/service_plan.md`에 정리했습니다.

포함 내용:

- 서비스 목적
- 타겟 사용자
- 페이지 구성
- 핵심 기능
- AI 입력/출력
- 실패 처리 기준
- 테스트 케이스

---

## 15. AI 코딩 도구 사용 증빙

AI 코딩 도구 사용 과정은 `docs/ai_coding_evidence.md`에 정리했습니다.  
실제 제출 시에는 대화 로그 또는 스크린샷을 추가합니다.

---

## 16. 보안 주의사항

- API 키는 절대 코드에 직접 작성하지 않습니다.
- API 키가 포함된 `.env` 파일은 GitHub에 올리지 않습니다.
- 키 유출이 의심되면 즉시 폐기하고 새 키를 발급합니다.
- 스크린샷에도 API 키가 보이지 않도록 주의합니다.

---

## 17. 향후 개선 방향

- 음성 파일 업로드 분석 기능 추가
- 발표 녹음 기반 발음/속도 분석
- 사용자별 분석 기록 저장
- 다크 모드 지원
- 방문자 분석 도구 연동
