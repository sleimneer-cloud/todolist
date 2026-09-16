from datetime import date, timedelta

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QDialog,
    QGraphicsOpacityEffect,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from todolist.data.repository import TaskRepository
from todolist.generated.ui_main_window import Ui_Dialog
from todolist.logic.geometry import compute_bottom_right_position
from todolist.logic.weekly_report import (
    MissingApiKeyError,
    WeeklyReportError,
    generate_weekly_report,
)
from todolist.widgets.add_task_dialog import AddTaskDialog
from todolist.widgets.task_row import TaskRow
from todolist.widgets.weekly_report_dialog import WeeklyReportDialog

SCREEN_MARGIN = 16


class _WeeklyReportWorker(QThread):
    """Groq 호출은 초 단위로 걸릴 수 있어, UI 스레드에서 직접 하면 그동안
    창이 멈춘다(마우스도 못 움직임) — QThread로 분리해서 백그라운드에서 돌린다.
    """

    succeeded = Signal(str)
    failed = Signal(str)

    def __init__(self, tasks, week_start: date, week_end: date, parent=None):
        super().__init__(parent)
        self._tasks = tasks
        self._week_start = week_start
        self._week_end = week_end

    def run(self) -> None:
        try:
            report = generate_weekly_report(self._tasks, self._week_start, self._week_end)
        except (MissingApiKeyError, WeeklyReportError) as e:
            self.failed.emit(str(e))
        else:
            self.succeeded.emit(report)


class TodoWindow(QDialog):
    def __init__(self, repository: TaskRepository, parent: QWidget | None = None):
        super().__init__(parent)
        self.repository = repository

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # Qt.Tool keeps the widget out of the dock/Cmd-Tab switcher, matching
        # a persistent desktop widget rather than a regular application window.
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        # macOS는 Qt.Tool 창을 앱이 비활성 상태가 되면 자동으로 숨긴다 — 다른
        # 앱을 클릭하는 순간 위젯이 통째로 사라지는 원인이었다. 이 속성이 그
        # 숨김을 막아서 정말로 "항상" 떠 있게 한다.
        self.setAttribute(Qt.WidgetAttribute.WA_MacAlwaysShowToolWindow)
        self.setFixedSize(self.size())

        # 핀 버튼: 꺼두면 일반 창처럼 동작(다른 창에 가려지고 비활성 시 숨음),
        # 켜두면 지금까지의 always-on-top 동작. .ui에서 기본 checked=True라
        # 위의 setWindowFlags/setAttribute 초기값과 이미 일치한다.
        self._pin_opacity = QGraphicsOpacityEffect(self.ui.pin_button)
        self.ui.pin_button.setGraphicsEffect(self._pin_opacity)
        self._pin_opacity.setOpacity(1.0)
        self.ui.pin_button.toggled.connect(self._on_pin_toggled)

        self._report_worker: _WeeklyReportWorker | None = None
        self.ui.report_button.clicked.connect(self._on_generate_report)

        # 행이 자기 위쪽에 구분선을 그리므로 레이아웃은 간격을 두지 않는다.
        self.list_layout = QVBoxLayout(self.ui.scrollAreaWidgetContents)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(0)
        self.list_layout.addStretch()

        self.ui.add_todo_button.clicked.connect(self._on_add_task)

        self._load_tasks()
        self._position_bottom_right()

    def _load_tasks(self) -> None:
        # done=True인 행도 DB엔 남아있다(주간 리포트용) — 목록 창에는 아직
        # 안 끝난 일만 보여준다.
        for task in self.repository.list():
            if not task.done:
                self._add_row(task)
        self._update_count()

    def _add_row(self, task) -> None:
        row = TaskRow(task, self.repository)
        row.deleted.connect(self._update_count)
        self.list_layout.insertWidget(self.list_layout.count() - 1, row)

    def _update_count(self) -> None:
        # 위젯 수명(deleteLater는 지연 삭제라 세는 시점이 애매하다)을 세는 대신
        # 저장소를 다시 센다. 삭제(또는 완료 처리)는 deleted 시그널 전에 이미
        # 커밋돼 있다. done인 행은 목록에 없으니 개수에서도 뺀다.
        remaining = sum(1 for t in self.repository.list() if not t.done)
        self.ui.count_label.setText(f"{remaining}개")

    def _on_add_task(self) -> None:
        dialog = AddTaskDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        text, start_date, due_date = dialog.values()
        if not text:
            return
        task = self.repository.add(text, due_date=due_date, start_date=start_date)
        self._add_row(task)
        self._update_count()

    def _on_pin_toggled(self, pinned: bool) -> None:
        # 실측 결과: macOS에서 Qt.Tool은 WindowStaysOnTopHint와 무관하게
        # 그 자체로 다른 창들 위에 뜬다 — Tool만 남기고 StaysOnTopHint를
        # 껐더니 여전히 Finder 창을 덮어버렸다(핀을 꺼도 안 꺼지던 원인).
        # 진짜로 "일반 창처럼" 만들려면 Tool 자체를 빼야 한다.
        flags = Qt.WindowType.FramelessWindowHint
        if pinned:
            flags |= Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint
        # setWindowFlags()는 실행 중인 창을 숨긴다 — 다시 show()해야 한다.
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_MacAlwaysShowToolWindow, pinned)
        self._pin_opacity.setOpacity(1.0 if pinned else 0.35)
        self.show()

    def _on_generate_report(self) -> None:
        # 캘린더상의 "이번 주 월~일"이 아니라, 버튼을 누른 시점부터 거꾸로
        # 6일 전까지 최근 7일을 가져온다 — 사람마다/업무마다 "한 주"의 경계가
        # 다르고(예: 지난주 목요일에 시작해 이번 주 화요일에 끝난 일), 고정된
        # 월~일 경계로 자르면 그 흐름이 끊긴다.
        today = date.today()
        week_start = today - timedelta(days=6)
        week_end = today
        tasks = self.repository.list_for_week(week_start, week_end)
        if not tasks:
            QMessageBox.information(
                self, "주간 업무일지", "이번 주에 등록된 할 일이 없습니다."
            )
            return

        self.ui.report_button.setEnabled(False)
        self.ui.report_button.setText("⏳")
        self._report_worker = _WeeklyReportWorker(tasks, week_start, week_end, self)
        self._report_worker.succeeded.connect(self._on_report_succeeded)
        self._report_worker.failed.connect(self._on_report_failed)
        self._report_worker.finished.connect(self._reset_report_button)
        self._report_worker.start()

    def _on_report_succeeded(self, report: str) -> None:
        WeeklyReportDialog(report, self).exec()

    def _on_report_failed(self, message: str) -> None:
        QMessageBox.critical(self, "주간 업무일지 생성 실패", message)

    def _reset_report_button(self) -> None:
        self.ui.report_button.setEnabled(True)
        self.ui.report_button.setText("📄")

    def _position_bottom_right(self) -> None:
        screen = QGuiApplication.primaryScreen().availableGeometry()
        x, y = compute_bottom_right_position(
            screen_width=screen.width(),
            screen_height=screen.height(),
            window_width=self.width(),
            window_height=self.height(),
            margin=SCREEN_MARGIN,
        )
        self.move(screen.x() + x, screen.y() + y)
