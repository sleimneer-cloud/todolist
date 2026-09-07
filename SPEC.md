# Spec: Desktop Todo Widget

## Objective
개인용으로 사용할, macOS 화면 우측 하단에 항상 고정되어 떠 있는 작은 할 일 목록 위젯.
클릭으로 완료 처리/수정/삭제가 가능하고, 마감 기한에 따라 항목 색상이 달라져 급한 일이 눈에 띄게 한다.
지금은 로컬 전용이지만, 나중에 계정 연동(동기화)을 붙일 수 있도록 데이터 접근 계층을 분리해 둔다.

- 사용자: 본인 (1인용, 로그인/계정 없음)
- 성공 기준: 화면에 늘 떠 있는 위젯에서 오늘 할 일을 추가하고, 완료 표시하고, 급한 항목을 색으로 바로 인지할 수 있다.

## Tech Stack
- Python 3.14 (이미 설치됨: `/opt/homebrew/bin/python3`)
- PySide6 (Qt for Python, LGPL) — UI
- SQLite (표준 라이브러리 `sqlite3`) — 로컬 저장
- pytest — 테스트
- ruff — lint + format (선택 도구, 의존성 최소화 목적)

**나중을 위한 확장 지점 (지금 구현 X):** 데이터 접근을 `TaskRepository` 인터페이스로 분리해서,
지금은 `LocalSqliteRepository`만 쓰고 나중에 계정 동기화가 필요해지면 FastAPI + MariaDB 기반
`RemoteRepository`를 같은 인터페이스로 구현해 교체할 수 있게 한다. FastAPI/MariaDB 서버 자체는
이번 스펙 범위 밖.

## Commands
```
가상환경 생성:  python3 -m venv .venv && source .venv/bin/activate
설치:          pip install -r requirements.txt
실행:          python -m todolist.main
테스트:        pytest
린트/포맷:      ruff check . --fix && ruff format .
```

## Project Structure
```
todolist/
├── src/todolist/
│   ├── main.py          # 앱 진입점 (QApplication 생성, 창 표시)
│   ├── window.py        # 프레임 없는 always-on-top 위젯 창, 우측 하단 위치 고정
│   ├── task_row.py       # 할 일 한 줄 위젯 (체크박스, 텍스트, 마감일, 삭제 버튼)
│   ├── models.py         # Task dataclass (id, text, due_date, done)
│   ├── repository.py     # TaskRepository 인터페이스 + LocalSqliteRepository 구현
│   └── db.py             # SQLite 연결 및 스키마 초기화
├── tests/
│   └── test_repository.py
├── requirements.txt
└── SPEC.md
```

## Code Style
PEP8, snake_case, 함수/메서드에 타입 힌트, 데이터 모델은 `dataclass` 사용.

```python
@dataclass
class Task:
    id: int | None
    text: str
    due_date: date | None
    done: bool = False

class TaskRepository(Protocol):
    def add(self, text: str, due_date: date | None) -> Task: ...
    def update(self, task_id: int, *, text: str | None = None,
               due_date: date | None = None, done: bool | None = None) -> Task: ...
    def delete(self, task_id: int) -> None: ...
    def list(self) -> list[Task]: ...
```

## Testing Strategy
- **pytest**로 `repository.py`(CRUD)와 마감일 긴급도 색상 판정 로직을 단위 테스트.
- UI(PySide6 위젯)는 GUI 테스트 프레임워크 없이 수동 확인으로 대체 (1인용 개인 도구 규모에 맞춰
  의존성을 늘리지 않음). 필요해지면 `pytest-qt` 도입을 나중에 고려.
- 커버리지 목표치는 따로 두지 않고, repository/색상 로직 경로를 빠짐없이 테스트하는 데 집중.

## Boundaries
- **Always**: 변경 시 항목 자동 저장(SQLite), 커밋 전 `pytest` 통과, repository 인터페이스를 통해서만
  데이터 접근 (UI 코드가 SQLite를 직접 건드리지 않음)
- **Ask first**: PySide6/pytest/ruff 외 새 의존성 추가, SQLite 스키마의 하위 호환 깨지는 변경,
  FastAPI/MariaDB 서버 착수
- **Never**: 자격 증명/비밀 값 커밋 (나중에 계정 연동 시 특히 중요), 실패하는 테스트를 승인 없이 삭제,
  경로를 하드코딩 (OS 표준 사용자 데이터 경로 사용)

## Success Criteria
1. 앱 실행 시 프레임 없는 작은 창이 화면 우측 하단에 always-on-top으로 고정되어 뜬다.
2. 할 일 텍스트(+선택적 마감일)를 입력해 추가할 수 있다.
3. 체크박스 클릭으로 완료 처리(취소선 표시), 텍스트 클릭으로 인라인 수정, × 버튼으로 삭제가 된다.
4. 앱을 껐다 켜도 목록이 SQLite에 저장되어 그대로 남아 있다.
5. 마감일 긴급도에 따라 항목 색이 달라진다 (아래 기본값, 조정 가능):
   - **기한 지남 / 오늘까지**: 눈에 띄는 색 (예: 빨강 계열)
   - **1~3일 남음**: 중간 톤 (예: 주황/노랑)
   - **4일 이상 남음 또는 마감일 없음**: 눈에 덜 띄는 색 (예: 회색 계열)
6. `pytest` 전체 통과, repository는 인터페이스 뒤에 있어 향후 원격 구현으로 교체 가능한 구조.

## Open Questions
- 색상 구간(오늘/1~3일/4일 이상)의 정확한 임계값과 실제 색상 코드는 구현 시 확정 — 위 기본값으로
  진행해도 괜찮은지 확인 필요.
- 카테고리/여러 목록 지원 여부는 이번 범위에는 없음 (필요해지면 추후 별도 스펙).
