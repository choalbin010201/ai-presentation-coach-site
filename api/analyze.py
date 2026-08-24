import json
import os
import re
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

try:
    from google import genai
except Exception:
    genai = None


def estimate_presentation_time(script):
    """
    한국어 발표 기준 대략 1분에 330~380자 정도로 계산.
    여기서는 평균 350자/분 기준으로 추정한다.
    """
    text = script.strip()
    char_count = len(text)

    if char_count == 0:
        return {
            "minutes": 0,
            "seconds": 0,
            "text": "0분 0초",
            "char_count": 0
        }

    total_minutes = char_count / 350
    minutes = int(total_minutes)
    seconds = int((total_minutes - minutes) * 60)

    return {
        "minutes": minutes,
        "seconds": seconds,
        "text": f"{minutes}분 {seconds}초",
        "char_count": char_count
    }


def fallback_analysis(topic, script, presentation_type, target_time):
    """
    Gemini API 호출 실패 시 기본 분석 결과를 반환한다.
    과제 제출 시 API 오류 대응 로직으로 설명 가능하다.
    """
    estimated = estimate_presentation_time(script)

    return {
        "used_fallback": True,
        "estimated_time_text": estimated["text"],
        "estimated_time": estimated,
        "analysis": {
            "score": {
                "total": 72,
                "structure": 70,
                "clarity": 75,
                "persuasiveness": 70,
                "delivery": 73
            },
            "structure_analysis": {
                "intro": "발표 주제가 제시되어 있으나, 청중의 관심을 끌 수 있는 문제 제기가 더 명확하면 좋습니다.",
                "body": "핵심 내용은 포함되어 있지만, 근거와 예시를 구분하면 전달력이 높아집니다.",
                "conclusion": "마무리 부분에서 핵심 메시지를 한 번 더 요약하면 발표 완성도가 올라갑니다.",
                "overall": "전체적으로 발표 흐름은 있으나 도입-본론-결론의 구분을 더 분명히 하면 좋습니다."
            },
            "strengths": [
                "발표 주제가 명확하게 설정되어 있습니다.",
                "핵심 내용을 직접적으로 전달하려는 방향이 좋습니다.",
                "대본 기반 발표 연습에 적합한 형태입니다."
            ],
            "improvements": [
                "도입부에 청중의 관심을 끌 수 있는 질문이나 상황 제시를 추가하세요.",
                "본론에서는 핵심 주장마다 구체적인 예시를 붙이면 좋습니다.",
                "결론에서는 발표 내용을 요약하고 마지막 메시지를 강조하세요."
            ],
            "revised_script": (
                f"안녕하세요. 오늘 발표할 주제는 '{topic}'입니다. "
                "이 주제는 우리가 실제 상황에서 자주 마주할 수 있는 문제와 연결되어 있습니다. "
                "먼저 현재 상황과 문제점을 살펴보고, 그다음 해결 방향과 기대 효과를 설명드리겠습니다. "
                "마지막으로 발표 내용을 정리하면서 이 주제가 왜 중요한지 다시 한 번 말씀드리겠습니다."
            ),
            "expected_questions": [
                {
                    "question": "이 발표 주제를 선택한 이유는 무엇인가요?",
                    "answer": "실제 문제 상황과 연결되어 있고, 청중이 쉽게 공감할 수 있는 주제라고 판단했기 때문입니다."
                },
                {
                    "question": "가장 중요한 핵심 메시지는 무엇인가요?",
                    "answer": "단순한 정보 전달이 아니라 문제를 이해하고 개선 방향을 제안하는 것입니다."
                },
                {
                    "question": "발표 시간을 맞추기 위해 어떤 부분을 조정할 수 있나요?",
                    "answer": "예시 설명을 줄이거나 결론 요약 부분을 압축하면 목표 시간에 맞출 수 있습니다."
                }
            ],
            "checklist": [
                "도입부에서 발표 목적을 분명히 말했는가?",
                "본론에서 핵심 내용을 2~3개로 나누었는가?",
                "각 주장에 예시나 근거가 있는가?",
                "결론에서 핵심 메시지를 다시 강조했는가?",
                "목표 발표 시간에 맞게 대본 길이를 조절했는가?"
            ],
            "one_sentence_summary": "발표 구조를 더 명확히 나누고 결론에서 핵심 메시지를 강조하면 완성도가 높아집니다."
        }
    }


def extract_json_from_text(text):
    """
    Gemini 응답에서 JSON 부분만 추출한다.
    모델이 ```json ... ``` 형태로 반환하는 경우도 처리한다.
    """
    if not text:
        raise ValueError("Empty AI response")

    cleaned = text.strip()

    cleaned = re.sub(r"^```json", "", cleaned)
    cleaned = re.sub(r"^```", "", cleaned)
    cleaned = re.sub(r"```$", "", cleaned)
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{[\s\S]*\}", cleaned)
    if match:
        return json.loads(match.group(0))

    raise ValueError("No JSON object found in AI response")


def analyze_with_gemini(topic, script, presentation_type, target_time):
    api_key = os.environ.get("GEMINI_API_KEY")
    model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is missing.")

    if genai is None:
        raise ValueError("google-genai package is not installed.")

    estimated = estimate_presentation_time(script)

    client = genai.Client(api_key=api_key)

    prompt = f"""
너는 발표 코칭 전문가야.
사용자의 발표 대본을 분석하고, 반드시 JSON 형식으로만 응답해.

[발표 정보]
- 발표 주제: {topic}
- 발표 유형: {presentation_type}
- 목표 발표 시간: {target_time}분
- 예상 발표 시간: {estimated["text"]}
- 대본 글자 수: {estimated["char_count"]}자

[발표 대본]
{script}

아래 JSON 구조를 반드시 지켜서 응답해.
설명 문장이나 마크다운 없이 JSON만 반환해.

{{
  "score": {{
    "total": 0,
    "structure": 0,
    "clarity": 0,
    "persuasiveness": 0,
    "delivery": 0
  }},
  "structure_analysis": {{
    "intro": "",
    "body": "",
    "conclusion": "",
    "overall": ""
  }},
  "strengths": ["", "", ""],
  "improvements": ["", "", ""],
  "revised_script": "",
  "expected_questions": [
    {{
      "question": "",
      "answer": ""
    }},
    {{
      "question": "",
      "answer": ""
    }},
    {{
      "question": "",
      "answer": ""
    }}
  ],
  "checklist": ["", "", "", "", ""],
  "one_sentence_summary": ""
}}
"""

    response = client.models.generate_content(
        model=model_name,
        contents=prompt
    )

    response_text = response.text
    analysis = extract_json_from_text(response_text)

    return {
        "used_fallback": False,
        "estimated_time_text": estimated["text"],
        "estimated_time": estimated,
        "analysis": analysis
    }


class handler(BaseHTTPRequestHandler):
    def _send_json(self, data, status_code=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, text, status_code=200):
        self.send_response(status_code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(text.encode("utf-8"))

    def _serve_file(self, file_path, content_type):
        if not os.path.exists(file_path):
            self._send_text("Not Found", 404)
            return

        with open(file_path, "rb") as file:
            content = file.read()

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(content)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        """
        현재 Vercel이 루트 요청까지 Python handler로 보내고 있어서,
        GET 요청에서 직접 index.html, css, js를 서빙하도록 처리한다.
        """
        try:
            parsed_url = urlparse(self.path)
            path = parsed_url.path

            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

            if path == "/" or path == "/index.html":
                file_path = os.path.join(base_dir, "index.html")
                self._serve_file(file_path, "text/html; charset=utf-8")
                return

            if path == "/css/style.css":
                file_path = os.path.join(base_dir, "css", "style.css")
                self._serve_file(file_path, "text/css; charset=utf-8")
                return

            if path == "/js/main.js":
                file_path = os.path.join(base_dir, "js", "main.js")
                self._serve_file(file_path, "application/javascript; charset=utf-8")
                return

            if path == "/api/analyze":
                self._send_json({
                    "service": "AI 발표 코치 API",
                    "status": "ok",
                    "message": "POST 요청으로 발표 주제와 대본을 보내면 분석 결과를 반환합니다."
                })
                return

            self._send_text("Not Found", 404)

        except Exception as error:
            self._send_text(f"Server error: {str(error)}", 500)

    def do_POST(self):
        try:
            parsed_url = urlparse(self.path)
            path = parsed_url.path

            if path != "/api/analyze" and path != "/":
                self._send_json({
                    "error": "지원하지 않는 API 경로입니다."
                }, 404)
                return

            content_length = int(self.headers.get("Content-Length", 0))
            raw_body = self.rfile.read(content_length).decode("utf-8")

            try:
                body = json.loads(raw_body)
            except json.JSONDecodeError:
                self._send_json({
                    "error": "요청 본문이 올바른 JSON 형식이 아닙니다."
                }, 400)
                return

            topic = str(body.get("topic", "")).strip()
            script = str(body.get("script", "")).strip()
            presentation_type = str(body.get("presentation_type", "일반 발표")).strip()
            target_time = body.get("target_time", 3)

            if not topic:
                self._send_json({
                    "error": "발표 주제를 입력해주세요."
                }, 400)
                return

            if not script:
                self._send_json({
                    "error": "발표 대본을 입력해주세요."
                }, 400)
                return

            if len(script) < 50:
                self._send_json({
                    "error": "대본이 너무 짧습니다. 최소 50자 이상 입력해주세요."
                }, 400)
                return

            try:
                result = analyze_with_gemini(
                    topic=topic,
                    script=script,
                    presentation_type=presentation_type,
                    target_time=target_time
                )
            except Exception as api_error:
                result = fallback_analysis(
                    topic=topic,
                    script=script,
                    presentation_type=presentation_type,
                    target_time=target_time
                )
                result["api_error"] = str(api_error)

            self._send_json(result)

        except Exception as error:
            self._send_json({
                "error": f"서버 오류가 발생했습니다: {str(error)}"
            }, 500)