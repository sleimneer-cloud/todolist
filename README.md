# TodoList

macOS 화면 우측 하단에 항상 떠 있는 개인용 할 일 위젯. 프레임 없이 항상 위(always-on-top)로
고정되어, 마감일이 가까운 항목일수록 눈에 띄는 색으로 표시된다.

## 요구 사항

- **Apple Silicon Mac** (M1 이상) — 배포된 빌드는 arm64 전용, Intel Mac에서는 실행 불가
- **macOS 14 (Sonoma) 이상**

## 실행 방법

### 릴리즈로 받아서 쓰기 (추천)

1. [Releases](https://github.com/sleimneer-cloud/todolist/releases)에서 최신 `TodoList-*.zip` 다운로드 후 압축 해제
2. `TodoList.app`을 `Applications` 폴더로 이동
3. 코드 서명이 안 된 빌드라 첫 실행 시 macOS가 **"확인되지 않은 개발자"** 경고를 띄운다:
   - `TodoList.app`을 **우클릭(Control+클릭) → 열기** → 뜨는 경고창에서 다시 **열기**
   - 그래도 막히면: **시스템 설정 → 개인정보 보호 및 보안** 하단의 **"그래도 열기"** 클릭
   - 그래도 안 되면 터미널에서: `xattr -cr /Applications/TodoList.app`
4. 이후로는 그냥 더블클릭하면 실행된다.

### 소스에서 직접 실행 (개발용)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src python -m todolist.main
```

## 사용법

- 화면 우하단에 창이 뜨면 **"일정 추가"** 버튼 클릭
- 모달에서 **할일 내용 / 시작일 / 마감일시**를 입력하고 저장
- 목록에서 **체크박스**를 클릭하면 확인 없이 즉시 삭제, **텍스트 클릭**으로 인라인 수정, **×** 버튼으로도 삭제 가능
- 창은 크기 조절/드래그가 되지 않으며, 재시작해도 기존 목록이 그대로 유지된다 (SQLite 로컬 저장)

## 현재 기능

- 프레임 없는 always-on-top 위젯, 화면 우하단 고정 — 헤더의 📌 버튼으로 껐다 켰다 가능
- 할 일 추가 (내용 / 시작일 / 마감일시)
- 체크 시 즉시 삭제(완료 처리), 인라인 텍스트 수정, × 버튼 삭제
- 마감일 기준 색상 표시: 오늘 이후 마감(지남 포함) `빨강` · 3일 이내 `주황` · 그 외/마감일 없음 `회색`
  (색상 판정은 날짜 단위이며 마감 시각은 판정에 영향을 주지 않는다)
- SQLite 로컬 영구 저장 (앱 재시작해도 유지)
- 헤더의 📄 버튼으로 이번 주(월~일) 할 일을 모아 LLM에게 주간 업무일지를 요약시킴 (아래 "주간 업무일지" 참고)

## 주간 업무일지 (Groq)

📄 버튼을 누르면 이번 주에 등록된 할 일을 [Groq](https://console.groq.com) LLM에 보내 3~5문장짜리
업무일지를 만들어준다. Anthropic API는 비용 때문에 쓰지 않고, 무료 티어가 있는 Groq의
OpenAI 호환 Chat Completions API를 stdlib `urllib`로 직접 호출한다 (새 의존성 없음).

사용하려면 API 키를 환경변수로 설정해야 한다:

```bash
export GROQ_API_KEY="여기에_키"
```

키는 [console.groq.com](https://console.groq.com/keys)에서 발급받는다. 코드/DB에는 저장하지 않고
환경변수로만 읽으므로, `.zshrc` 등에 등록해두거나 앱 실행 전 셸에서 export한다. `.app`을 더블클릭으로
실행하는 경우 GUI 앱은 셸의 환경변수를 상속받지 못할 수 있다 — 그럴 땐 `launchctl setenv
GROQ_API_KEY "여기에_키"`로 세션 전역에 등록하거나, 터미널에서 소스 실행 방식을 쓴다.

키가 없으면 버튼을 눌러도 네트워크 요청 없이 바로 안내 메시지가 뜬다. 모델은 기본값
(`llama-3.3-70b-versatile`)을 쓰며, 다른 모델로 바꾸려면 `GROQ_MODEL` 환경변수를 설정한다 — 현재
사용 가능한 모델 목록은 [console.groq.com/docs/models](https://console.groq.com/docs/models)에서 확인.

## 개발

```bash
pytest          # 테스트
ruff check .    # 린트
```

Qt Designer로 `.ui` 수정 후 코드 재생성 (`src/todolist/ui/`가 디자인 소스, `src/todolist/ui_*.py`는 생성물이라 직접 수정 금지):

```bash
pyside6-uic src/todolist/ui/main_window.ui -o src/todolist/ui_main_window.py
pyside6-uic src/todolist/ui/add_task_dialog.ui -o src/todolist/ui_add_task_dialog.py
```

`.app` 재빌드:

```bash
pyinstaller TodoList.spec --noconfirm
```

`TodoList.spec`을 지우고 `pyinstaller --windowed ...`로 새로 생성하지 말 것 — `style.qss`를 번들에 포함시키는 `datas` 설정이 스크립트에서 새로 생성한 spec에는 없어서, 앱이 조용히 기본(디자인 없는) 모습으로 돌아간다.
