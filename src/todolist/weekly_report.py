"""한 주간의 할 일을 Groq LLM에 보내 짧은 업무일지로 요약한다.

Qt를 import하지 않는다 — window.py가 UI 스레드를 막지 않으려고 별도
스레드에서 이 모듈을 호출한다 (task_row.py 등 Qt 위젯 모듈과 달리 순수
로직만 담아 그 스레드 분리를 가능하게 한다).
"""

import json
import os
import urllib.error
import urllib.request
from datetime import date

from todolist.db import DEFAULT_DB_PATH
from todolist.models import Task

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
# Groq는 무료 모델 라인업이 자주 바뀐다 — 최신 목록은
# https://console.groq.com/docs/models 에서 확인하고, 다른 모델을 쓰려면
# GROQ_MODEL 환경변수로 덮어쓴다.
DEFAULT_MODEL = "llama-3.3-70b-versatile"
REQUEST_TIMEOUT_SECONDS = 30

# 프롬프트 문구를 코드가 아니라 텍스트 파일로 보관 — 사용자가 코드를 고치지
# 않고도 이 파일만 열어서 문구를 바꿀 수 있다. DB와 같은 디렉터리에 둔다.
# {week_start}/{week_end}/{task_block} 세 자리표시자를 채워 넣는다 (README 참고).
PROMPT_TEMPLATE_PATH = DEFAULT_DB_PATH.parent / "weekly_report_prompt.txt"
DEFAULT_PROMPT_TEMPLATE = (
    "{week_start} ~ {week_end} 한 주간의 할 일 목록:\n\n"
    "{task_block}\n\n"
    "위 목록을 바탕으로 이번 주 업무를 요약하는 한국어 주간 업무일지를 "
    "3~5문장으로 작성해줘. 목록을 그대로 나열하지 말고 자연스러운 "
    "문장으로 정리해줘."
)


def _load_prompt_template() -> str:
    if not PROMPT_TEMPLATE_PATH.exists():
        PROMPT_TEMPLATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        PROMPT_TEMPLATE_PATH.write_text(DEFAULT_PROMPT_TEMPLATE, encoding="utf-8")
    return PROMPT_TEMPLATE_PATH.read_text(encoding="utf-8")


class MissingApiKeyError(Exception):
    """GROQ_API_KEY 환경변수가 설정되어 있지 않다."""


class WeeklyReportError(Exception):
    """네트워크 오류, API 오류 등 리포트 생성 실패."""


def _build_prompt(tasks: list[Task], week_start: date, week_end: date) -> str:
    if not tasks:
        task_block = "(이번 주에 등록된 할 일이 없습니다)"
    else:
        lines = []
        for t in tasks:
            line = f"- [{'완료' if t.done else '미완료'}] {t.text}"
            if t.due_date:
                line += f" (마감 {t.due_date:%m-%d %H:%M})"
            lines.append(line)
        task_block = "\n".join(lines)

    template = _load_prompt_template()
    return template.format(
        week_start=f"{week_start:%Y-%m-%d}",
        week_end=f"{week_end:%Y-%m-%d}",
        task_block=task_block,
    )


def generate_weekly_report(
    tasks: list[Task], week_start: date, week_end: date
) -> str:
    """Groq Chat Completions API(OpenAI 호환)를 호출해 리포트 문자열을 만든다.

    API 문서: https://console.groq.com/docs/api-reference#chat-create
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise MissingApiKeyError("GROQ_API_KEY 환경변수가 설정되어 있지 않습니다.")

    model = os.environ.get("GROQ_MODEL", DEFAULT_MODEL)
    payload = json.dumps(
        {
            "model": model,
            "messages": [
                {"role": "user", "content": _build_prompt(tasks, week_start, week_end)}
            ],
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        GROQ_API_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            body = json.loads(response.read())
    except urllib.error.HTTPError as e:
        # 4xx/5xx — 응답 바디에 Groq가 사람이 읽을 에러 메시지를 담아준다.
        detail = e.read().decode("utf-8", errors="replace")
        raise WeeklyReportError(f"Groq API 오류 ({e.code}): {detail}") from e
    except urllib.error.URLError as e:
        # DNS 실패, 연결 거부, 타임아웃 등 요청이 아예 도달하지 못한 경우.
        raise WeeklyReportError(f"네트워크 오류: {e.reason}") from e

    try:
        return body["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError) as e:
        raise WeeklyReportError(f"예상치 못한 응답 형식: {body}") from e
