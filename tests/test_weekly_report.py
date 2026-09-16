import json
import urllib.error
from datetime import date, datetime
from unittest.mock import MagicMock, patch

import pytest

from todolist.models import Task
from todolist.weekly_report import (
    MissingApiKeyError,
    WeeklyReportError,
    generate_weekly_report,
)

WEEK_START = date(2026, 9, 14)
WEEK_END = date(2026, 9, 20)


def _task(text: str, done: bool = False) -> Task:
    return Task(id=1, text=text, due_date=None, done=done)


def test_missing_api_key_raises_without_calling_network(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with patch("todolist.weekly_report.urllib.request.urlopen") as mock_urlopen:
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
    with patch("todolist.weekly_report.urllib.request.urlopen", return_value=_mock_response(body)):
        result = generate_weekly_report([_task("보고서 작성")], WEEK_START, WEEK_END)
    assert result == "이번 주 요약입니다."


def test_http_error_wrapped_as_weekly_report_error(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    error = urllib.error.HTTPError(
        url="", code=401, msg="Unauthorized", hdrs=None, fp=MagicMock()
    )
    error.fp.read.return_value = b'{"error": "invalid api key"}'
    with (
        patch("todolist.weekly_report.urllib.request.urlopen", side_effect=error),
        pytest.raises(WeeklyReportError, match="401"),
    ):
        generate_weekly_report([_task("a")], WEEK_START, WEEK_END)


def test_network_error_wrapped_as_weekly_report_error(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    error = urllib.error.URLError("연결할 수 없음")
    with (
        patch("todolist.weekly_report.urllib.request.urlopen", side_effect=error),
        pytest.raises(WeeklyReportError),
    ):
        generate_weekly_report([_task("a")], WEEK_START, WEEK_END)


def test_unexpected_response_shape_wrapped_as_weekly_report_error(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    with patch(
        "todolist.weekly_report.urllib.request.urlopen",
        return_value=_mock_response({"unexpected": "shape"}),
    ), pytest.raises(WeeklyReportError):
        generate_weekly_report([_task("a")], WEEK_START, WEEK_END)


def test_empty_week_still_builds_a_valid_prompt(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    body = {"choices": [{"message": {"content": "할 일이 없었어요."}}]}
    with patch("todolist.weekly_report.urllib.request.urlopen", return_value=_mock_response(body)) as m:
        generate_weekly_report([], WEEK_START, WEEK_END)
    sent_body = json.loads(m.call_args[0][0].data)
    assert "없습니다" in sent_body["messages"][0]["content"]


def test_due_date_included_in_prompt(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    task = Task(id=1, text="발표 준비", due_date=datetime(2026, 9, 18, 14, 0))
    body = {"choices": [{"message": {"content": "ok"}}]}
    with patch("todolist.weekly_report.urllib.request.urlopen", return_value=_mock_response(body)) as m:
        generate_weekly_report([task], WEEK_START, WEEK_END)
    sent_body = json.loads(m.call_args[0][0].data)
    assert "발표 준비" in sent_body["messages"][0]["content"]
    assert "09-18 14:00" in sent_body["messages"][0]["content"]
