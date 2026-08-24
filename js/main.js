const navToggle = document.querySelector(".nav-toggle");
const navLinks = document.querySelector(".nav-links");
const form = document.querySelector("#coachForm");
const topicInput = document.querySelector("#topic");
const scriptInput = document.querySelector("#script");
const charCount = document.querySelector("#charCount");
const formMessage = document.querySelector("#formMessage");
const analyzeButton = document.querySelector("#analyzeButton");
const loadingBox = document.querySelector("#loadingBox");
const emptyResult = document.querySelector("#emptyResult");
const resultBox = document.querySelector("#resultBox");

if (navToggle && navLinks) {
  navToggle.addEventListener("click", () => {
    navLinks.classList.toggle("open");
  });
}

document.querySelectorAll(".nav-links a").forEach((link) => {
  link.addEventListener("click", () => {
    navLinks.classList.remove("open");
  });
});

if (scriptInput && charCount) {
  scriptInput.addEventListener("input", () => {
    charCount.textContent = `${scriptInput.value.trim().length}자`;
  });
}

if (form) {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearMessage();

    const payload = {
      topic: topicInput.value.trim(),
      script: scriptInput.value.trim(),
      presentation_type: document.querySelector("#presentationType").value,
      target_time: Number(document.querySelector("#targetTime").value)
    };

    if (!payload.topic || !payload.script) {
      showMessage("발표 주제와 발표 대본을 모두 입력해주세요.");
      return;
    }

    if (payload.script.length < 50) {
      showMessage("대본이 너무 짧습니다. 최소 50자 이상 입력해주세요.");
      return;
    }

    setLoading(true);

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 45000);

      const response = await fetch("/api/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      let data;
      try {
        data = await response.json();
      } catch (jsonError) {
        throw new Error("서버 응답을 JSON으로 읽을 수 없습니다.");
      }

      if (!response.ok) {
        throw new Error(data.error || "AI 분석 중 오류가 발생했습니다.");
      }

      renderResult(data);
    } catch (error) {
      if (error.name === "AbortError") {
        showMessage("AI 응답이 지연되고 있습니다. 잠시 후 다시 시도해주세요.");
      } else {
        showMessage(error.message || "잠시 후 다시 시도해주세요.");
      }
    } finally {
      setLoading(false);
    }
  });
}

function clearMessage() {
  if (formMessage) {
    formMessage.textContent = "";
  }
}

function showMessage(message) {
  if (formMessage) {
    formMessage.textContent = message;
  }
}

function setLoading(isLoading) {
  if (analyzeButton) {
    analyzeButton.disabled = isLoading;
    analyzeButton.textContent = isLoading ? "분석 중..." : "AI 분석 시작";
  }

  if (loadingBox) {
    loadingBox.classList.toggle("hidden", !isLoading);
  }

  if (isLoading) {
    if (emptyResult) {
      emptyResult.classList.add("hidden");
    }

    if (resultBox) {
      resultBox.classList.add("hidden");
    }
  }
}

function renderResult(data) {
  if (!resultBox) {
    return;
  }

  if (emptyResult) {
    emptyResult.classList.add("hidden");
  }

  resultBox.classList.remove("hidden");

  const analysis = data.analysis || {};
  const score = analysis.score || {};
  const structure = analysis.structure_analysis || {};
  const questions = Array.isArray(analysis.expected_questions)
    ? analysis.expected_questions
    : [];

  resultBox.innerHTML = `
    ${
      data.used_fallback
        ? `<div class="notice">AI API 호출이 실패하여 기본 분석 결과를 표시했습니다. 실제 배포 환경에서는 환경 변수와 API 상태를 확인해주세요.</div>`
        : ""
    }

    <div class="result-summary">
      <div class="metric">
        <span>총점</span>
        <strong>${escapeHtml(score.total ?? "-")}</strong>
      </div>
      <div class="metric">
        <span>구조</span>
        <strong>${escapeHtml(score.structure ?? "-")}</strong>
      </div>
      <div class="metric">
        <span>명확성</span>
        <strong>${escapeHtml(score.clarity ?? "-")}</strong>
      </div>
      <div class="metric">
        <span>예상 시간</span>
        <strong>${escapeHtml(data.estimated_time_text || "-")}</strong>
      </div>
    </div>

    <section class="result-section">
      <h3>발표 구조 분석</h3>
      <p><strong>도입:</strong> ${escapeHtml(structure.intro || "-")}</p>
      <p><strong>본론:</strong> ${escapeHtml(structure.body || "-")}</p>
      <p><strong>결론:</strong> ${escapeHtml(structure.conclusion || "-")}</p>
      <p><strong>종합:</strong> ${escapeHtml(structure.overall || "-")}</p>
    </section>

    <section class="result-section">
      <h3>장점</h3>
      ${renderList(analysis.strengths)}
    </section>

    <section class="result-section">
      <h3>개선점</h3>
      ${renderList(analysis.improvements)}
    </section>

    <section class="result-section">
      <h3>수정 발표 대본</h3>
      <p class="revised-script">${escapeHtml(analysis.revised_script || "-")}</p>
    </section>

    <section class="result-section">
      <h3>예상 질문과 답변</h3>
      <ol>
        ${
          questions
            .map(
              (item) => `
                <li>
                  <strong>${escapeHtml(item.question || "예상 질문")}</strong><br />
                  <span>${escapeHtml(item.answer || "-")}</span>
                </li>
              `
            )
            .join("") || "<li>예상 질문이 없습니다.</li>"
        }
      </ol>
    </section>

    <section class="result-section">
      <h3>발표 전 체크리스트</h3>
      ${renderList(analysis.checklist)}
    </section>

    <section class="result-section">
      <h3>핵심 조언</h3>
      <p>${escapeHtml(analysis.one_sentence_summary || "-")}</p>
    </section>
  `;
}

function renderList(items) {
  if (!Array.isArray(items) || items.length === 0) {
    return "<p>-</p>";
  }

  return `
    <ul>
      ${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
    </ul>
  `;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}