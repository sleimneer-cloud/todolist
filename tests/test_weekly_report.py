import json
import urllib.error
from datetime import date, datetime
from unittest.mock import MagicMock, patch

import pytest

from todolist.data.models import Task
from todolist.logic.weekly_report import (
    MissingApiKeyError,
    WeeklyReportError,
    generate_weekly_report,
)

WEEK_START = date(2026, 9, 14)
WEEK_END = date(2026, 9, 20)


@pytest.fixture(autouse=True)
def _isolated_prompt_template(tmp_path, monkeypatch):
    # 실제 사용자의 ~/Library 템플릿 파일을 읽거나 덮어쓰지 않도록, 매 테스트마다
    # 임시 경로로 바꿔치기한다 — 없으면 개발자가 커스터마이즈해둔 실제 파일을
    # 테스트가 읽어버려 결과가 머신마다 달라진다.
    monkeypatch.setattr(
        "todolist.logic.weekly_report.PROMPT_TEMPLATE_PATH", tmp_path / "weekly_report_prompt.txt"
    )


def _task(text: str, done: bool = False) -> Task:
    return Task(id=1, text=text, due_date=None, done=done)


def test_missing_api_key_raises_without_calling_network(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with patch("todolist.logic.weekly_report.urllib.request.urlopen") as mock_urlopen:
        with pytest.raises(MissingApiKeyError):
            generate_weekly_report([_task("a")], WEEK_START, WEEK_END)
        mock_urlopen.assert_not_called()


def _mock_response(body: dict):
    response = MagicMock()
    response.read.return_value = json.dumps(body).encode("utf-8")
    response.__enter__.return_value = response
    return response


def test_generate_weekly_report_returns_message_content(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    body = {"choices": [{"message": {"content": "  이번 주 요약입니다.  "}}]}
    with patch("todolist.logic.weekly_report.urllib.request.urlopen", return_value=_mock_response(body)):
        result = generate_weekly_report([_task("보고서 작성")], WEEK_START, WEEK_END)
    assert result == "이번 주 요약입니다."


def test_request_sends_a_user_agent(monkeypatch):
    # urllib의 기본 요청(User-Agent 없음)은 Groq 앞단 Cloudflare가 봇으로 보고
    # 403(error code: 1010)으로 차단한다 — 실제로 재현/수정한 회귀 방지 테스트.
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    body = {"choices": [{"message": {"content": "ok"}}]}
    with patch("todolist.logic.weekly_report.urllib.request.urlopen", return_value=_mock_response(body)) as m:
        generate_weekly_report([_task("a")], WEEK_START, WEEK_END)
    sent_request = m.call_args[0][0]
    assert sent_request.get_header("User-agent")


def test_http_error_wrapped_as_weekly_report_error(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    error = urllib.error.HTTPError(
        url="", code=401, msg="Unauthorized", hdrs=None, fp=MagicMock()
    )
    error.fp.read.return_value = b'{"error": "invalid api key"}'
    with (
        patch("todolist.logic.weekly_report.urllib.request.urlopen", side_effect=error),
        pytest.raises(WeeklyReportError, match="401"),
    ):
        generate_weekly_report([_task("a")], WEEK_START, WEEK_END)


def test_network_error_wrapped_as_weekly_report_error(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    error = urllib.error.URLError("연결할 수 없음")
    with (
        patch("todolist.logic.weekly_report.urllib.request.urlopen", side_effect=error),
        pytest.raises(WeeklyReportError),
    ):
        generate_weekly_report([_task("a")], WEEK_START, WEEK_END)


def test_unexpected_response_shape_wrapped_as_weekly_report_error(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    with patch(
        "todolist.logic.weekly_report.urllib.request.urlopen",
        return_value=_mock_response({"unexpected": "shape"}),
    ), pytest.raises(WeeklyReportError):
        generate_weekly_report([_task("a")], WEEK_START, WEEK_END)


def test_empty_week_still_builds_a_valid_prompt(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    body = {"choices": [{"message": {"content": "할 일이 없었어요."}}]}
    with patch("todolist.logic.weekly_report.urllib.request.urlopen", return_value=_mock_response(body)) as m:
        generate_weekly_report([], WEEK_START, WEEK_END)
    sent_body = json.loads(m.call_args[0][0].data)
    assert "없습니다" in sent_body["messages"][0]["content"]


def test_due_date_included_in_prompt(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    task = Task(id=1, text="발표 준비", due_date=datetime(2026, 9, 18, 14, 0))
    body = {"choices": [{"message": {"content": "ok"}}]}
    with patch("todolist.logic.weekly_report.urllib.request.urlopen", return_value=_mock_response(body)) as m:
        generate_weekly_report([task], WEEK_START, WEEK_END)
    sent_body = json.loads(m.call_args[0][0].data)
    assert "발표 준비" in sent_body["messages"][0]["content"]
    assert "09-18 14:00" in sent_body["messages"][0]["content"]


def test_prompt_template_file_created_with_default_on_first_use(tmp_path, monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    template_path = tmp_path / "weekly_report_prompt.txt"
    monkeypatch.setattr("todolist.logic.weekly_report.PROMPT_TEMPLATE_PATH", template_path)
    assert not template_path.exists()

    body = {"choices": [{"message": {"content": "ok"}}]}
    with patch("todolist.logic.weekly_report.urllib.request.urlopen", return_value=_mock_response(body)):
        generate_weekly_report([_task("a")], WEEK_START, WEEK_END)

    assert template_path.exists()
    from todolist.logic.weekly_report import DEFAULT_PROMPT_TEMPLATE

    assert template_path.read_text(encoding="utf-8") == DEFAULT_PROMPT_TEMPLATE


def test_editing_template_file_changes_the_sent_prompt(tmp_path, monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    template_path = tmp_path / "weekly_report_prompt.txt"
    template_path.write_text(
        "커스텀 템플릿 — {week_start}부터 {week_end}까지.\n{task_block}", encoding="utf-8"
    )
    monkeypatch.setattr("todolist.logic.weekly_report.PROMPT_TEMPLATE_PATH", template_path)

    body = {"choices": [{"message": {"content": "ok"}}]}
    with patch("todolist.logic.weekly_report.urllib.request.urlopen", return_value=_mock_response(body)) as m:
        generate_weekly_report([_task("커스텀 확인용")], WEEK_START, WEEK_END)

    sent_body = json.loads(m.call_args[0][0].data)
    sent_prompt = sent_body["messages"][0]["content"]
    assert "커스텀 템플릿" in sent_prompt
    assert "커스텀 확인용" in sent_prompt
