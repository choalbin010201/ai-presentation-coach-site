# AI 코딩 도구 사용 증빙

이 문서는 AI 코딩 도구를 사용한 과정을 정리하기 위한 제출용 템플릿입니다.
실제 제출 시에는 대화 캡처 또는 로그를 추가합니다.

## 1. 사용한 AI 코딩 도구

- ChatGPT

## 2. 사용 목적

- 기존 Streamlit 기반 발표 코치 아이디어를 Vercel 과제 구조로 변환
- HTML/CSS/JavaScript 프론트엔드 구성
- Vercel Python Serverless Function 백엔드 구성
- README와 서비스 기획서 작성
- API 오류 처리 방식 설계

## 3. 주요 요청 예시

```text
기존 AI 발표 코치 프로젝트를 HTML/CSS/JS + Vercel Python API 구조로 바꿔줘.
```

```text
발표 주제와 대본을 입력하면 Gemini API로 분석 결과를 반환하는 api/analyze.py를 만들어줘.
```

```text
이번 과제 요구사항에 맞는 README.md와 서비스 기획서를 작성해줘.
```

## 4. 수정 및 검토한 내용

- Streamlit UI를 제거하고 순수 HTML/CSS/JS 구조로 변경
- API 키가 코드에 노출되지 않도록 환경 변수 방식으로 수정
- 빈 입력, 짧은 대본, API 오류에 대한 실패 처리 추가
- 모바일 반응형 CSS 보완

## 5. 제출용 스크린샷

```text
screenshots/ai_coding_process.png
```
