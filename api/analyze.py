import json
import os
import re
from http.server import BaseHTTPRequestHandler

from google import genai


def estimate_time(script):
    char_count = len(script.replace(" ", "").replace("\n", ""))
    minutes = char_count / 350 if char_count else 0
    return char_count, minutes, int(minutes), int((minutes - int(minutes)) * 60)


def extract_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and start < end:
            return json.loads(text[start:end + 1])
        raise


def safe_score(value):
    try:
        score = int(float(value))
    except (TypeError, ValueError):
        score = 0
    return max(0, min(score, 100))


def normalize_analysis(data):
    score = data.get("score", {})
    data["score"] = {
        "total": safe_score(score.get("total", 0)),
        "structure": safe_score(score.get("structure", 0)),
        "clarity": safe_score(score.get("clarity", 0)),
        "delivery": safe_score(score.get("delivery", 0)),
        "qna_preparation": safe_score(score.get("qna_preparation", 0)),
    }
    data.setdefault("structure_analysis", {
        "intro": "도입부 분석 정보가 없습니다.",
        "body": "본론부 분석 정보가 없습니다.",
        "conclusion": "결론부 분석 정보가 없습니다.",
        "overall": "전체 구조 분석 정보가 없습니다.",
    })
    data.setdefault("strengths", [])
    data.setdefault("improvements", [])
    data.setdefault("revised_script", "")
    data.setdefault("expected_questions", [])
    data.setdefault("checklist", [])
    data.setdefault("one_sentence_summary", "")
    return data


def fallback_analysis(topic, script, target_time):
    _, minutes, _, _ = estimate_time(script)
    if minutes < target_time * 0.7:
        time_feedback = "목표 발표 시간에 비해 대본이 짧은 편입니다. 구체적인 사례나 설명을 추가하면 좋습니다."
    elif minutes > target_time * 1.3:
        time_feedback = "목표 발표 시간에 비해 대본이 긴 편입니다. 반복되는 문장이나 덜 중요한 내용을 줄이면 좋습니다."
    else:
        time_feedback = "목표 발표 시간과 비교했을 때 대본 길이는 적절한 편입니다."

    return {
        "structure_analysis": {
            "intro": "도입부에서는 발표 주제와 발표 목적을 더 명확하게 제시하는 것이 좋습니다.",
            "body": "본론부에서는 핵심 내용을 순서대로 나누어 설명하는 구성이 필요합니다.",
            "conclusion": "결론부에서는 발표 내용을 요약하고 핵심 메시지를 다시 강조하면 좋습니다.",
            "overall": f"기본 분석 모드입니다. {time_feedback}",
        },
        "score": {
            "total": 75,
            "structure": 70,
            "clarity": 75,
            "delivery": 75,
            "qna_preparation": 80,
        },
        "strengths": [
            "발표 주제와 대본을 입력하여 발표 준비 과정을 체계화했습니다.",
            "발표 내용을 글로 정리했기 때문에 말하기 연습의 기반이 마련되었습니다.",
            "예상 질문을 준비할 수 있는 형태로 발표 내용을 구성할 수 있습니다.",
        ],
        "improvements": [
            "도입부에서 발표 주제와 발표 목적을 더 명확하게 말하면 좋습니다.",
            "'먼저', '다음으로', '마지막으로' 같은 연결 표현을 사용하면 발표 흐름이 좋아집니다.",
            "마무리에서 핵심 내용을 한 문장으로 정리하고 청중에게 전달할 메시지를 강조하면 좋습니다.",
        ],
        "revised_script": f"""안녕하세요. 저는 오늘 {topic}에 대해 발표하겠습니다.
먼저 이 주제를 선택한 이유와 배경을 간단히 설명하겠습니다. 이 주제는 현재 우리 생활과 밀접하게 관련되어 있으며, 앞으로도 중요성이 커질 가능성이 있습니다.

다음으로 핵심 내용을 중심으로 발표를 진행하겠습니다. 발표 내용은 이해하기 쉽도록 주요 개념, 구체적인 예시, 그리고 활용 가능성 순서로 설명하겠습니다.

마지막으로 발표 내용을 정리하면, {topic}은 단순한 개념을 넘어 실제 문제 해결에 활용될 수 있는 중요한 주제입니다. 이상으로 발표를 마치겠습니다. 감사합니다.""",
        "expected_questions": [
            {
                "question": "이 주제를 선택한 가장 큰 이유는 무엇인가요?",
                "answer": "발표 준비 과정에서 실제로 겪는 문제를 해결할 수 있는 주제이기 때문입니다.",
            },
            {
                "question": "이 발표의 핵심 메시지는 무엇인가요?",
                "answer": "발표 내용을 구조화하고 반복적으로 점검하면 전달력을 높일 수 있다는 점입니다.",
            },
            {
                "question": "기존 발표 연습 방식과 비교했을 때 장점은 무엇인가요?",
                "answer": "혼자서도 반복적으로 피드백을 받을 수 있고 예상 질문까지 준비할 수 있다는 점입니다.",
            },
        ],
        "checklist": [
            "발표 주제가 첫 부분에 명확하게 제시되었는지 확인하기",
            "도입-본론-결론 구조가 드러나는지 확인하기",
            "예시나 사례가 포함되어 있는지 확인하기",
            "발표 시간이 목표 시간과 비슷한지 확인하기",
            "예상 질문에 대한 답변을 미리 준비하기",
        ],
        "one_sentence_summary": "발표는 내용을 잘 아는 것뿐만 아니라 청중이 이해하기 쉽게 구조화해서 전달하는 것이 중요합니다.",
    }


def analyze_with_gemini(topic, script, presentation_type, target_time):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")

    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    client = genai.Client(api_key=api_key)

    prompt = f"""
너는 대학생 발표를 도와주는 전문 AI 발표 코치이다.
사용자의 발표 대본을 분석하고 발표자가 실제로 개선할 수 있는 구체적인 피드백을 제공해라.

반드시 아래 JSON 형식으로만 답변해라.
마크다운 코드블록은 쓰지 마라.
설명 문장 없이 JSON만 출력해라.

발표 유형: {presentation_type}
발표 주제: {topic}
목표 발표 시간: {target_time}분

발표 대본:
{script}

분석 기준:
1. 도입-본론-결론 구조가 명확한지 평가
2. 발표 주제가 잘 드러나는지 평가
3. 대학 수업 발표에 적절한 표현인지 평가
4. 말로 발표했을 때 자연스러운지 평가
5. 발표 점수를 100점 만점으로 계산
6. 예상 질문 3~5개와 답변 예시 생성
7. 전체 대본을 더 자연스러운 발표체로 수정
8. 발표 전 확인할 체크리스트 생성

JSON 형식:
{{
  "structure_analysis": {{
    "intro": "도입부 분석",
    "body": "본론부 분석",
    "conclusion": "결론부 분석",
    "overall": "전체 구조 평가"
  }},
  "score": {{
    "total": 85,
    "structure": 80,
    "clarity": 85,
    "delivery": 80,
    "qna_preparation": 90
  }},
  "strengths": ["장점 1", "장점 2", "장점 3"],
  "improvements": ["개선점 1", "개선점 2", "개선점 3"],
  "revised_script": "수정된 발표 대본",
  "expected_questions": [{{"question": "예상 질문 1", "answer": "답변 예시 1"}}],
  "checklist": ["체크리스트 1", "체크리스트 2"],
  "one_sentence_summary": "핵심 조언"
}}
""".strip()

    response = client.models.generate_content(model=model_name, contents=prompt)
    return normalize_analysis(extract_json(response.text))


class handler(BaseHTTPRequestHandler):
    def _send_json(self, status_code, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send_json(200, {"ok": True})

    def do_GET(self):
        self._send_json(200, {
            "service": "AI 발표 코치 API",
            "status": "ok",
            "message": "POST 요청으로 발표 주제와 대본을 보내면 분석 결과를 반환합니다.",
        })

    def do_POST(self):
        try:
            raw = self.rfile.read(int(self.headers.get("Content-Length", 0))).decode("utf-8")
            payload = json.loads(raw or "{}")
            topic = str(payload.get("topic", "")).strip()
            script = str(payload.get("script", "")).strip()
            presentation_type = str(payload.get("presentation_type", "대학 수업 발표")).strip()
            target_time = int(payload.get("target_time", 5))

            if not topic or not script:
                return self._send_json(400, {"error": "발표 주제와 발표 대본을 모두 입력해주세요."})
            if len(script) < 50:
                return self._send_json(400, {"error": "발표 대본은 최소 50자 이상 입력해주세요."})

            char_count, minutes, minute_part, second_part = estimate_time(script)
            used_fallback = False
            api_error = None

            try:
                analysis = analyze_with_gemini(topic, script, presentation_type, target_time)
            except Exception as error:
                used_fallback = True
                api_error = str(error)
                analysis = fallback_analysis(topic, script, target_time)

            self._send_json(200, {
                "topic": topic,
                "presentation_type": presentation_type,
                "target_time": target_time,
                "char_count": char_count,
                "estimated_minutes": round(minutes, 2),
                "estimated_time_text": f"{minute_part}분 {second_part}초",
                "analysis": analysis,
                "used_fallback": used_fallback,
                "api_error": api_error,
            })
        except json.JSONDecodeError:
            self._send_json(400, {"error": "요청 JSON 형식이 올바르지 않습니다."})
        except Exception as error:
            self._send_json(500, {"error": "서버 처리 중 오류가 발생했습니다.", "detail": str(error)})
