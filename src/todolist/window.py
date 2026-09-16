from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QDialog, QVBoxLayout, QWidget

from todolist.add_task_dialog import AddTaskDialog
from todolist.geometry import compute_bottom_right_position
from todolist.repository import TaskRepository
from todolist.task_row import TaskRow
from todolist.ui_main_window import Ui_Dialog

SCREEN_MARGIN = 16


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
        self.setFixedSize(self.size())

        # 행이 자기 위쪽에 구분선을 그리므로 레이아웃은 간격을 두지 않는다.
        self.list_layout = QVBoxLayout(self.ui.scrollAreaWidgetContents)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(0)
        self.list_layout.addStretch()

        self.ui.add_todo_button.clicked.connect(self._on_add_task)

        self._load_tasks()
        self._position_bottom_right()

    def _load_tasks(self) -> None:
        for task in self.repository.list():
            self._add_row(task)
        self._update_count()

    def _add_row(self, task) -> None:
        row = TaskRow(task, self.repository)
        row.deleted.connect(self._update_count)
        self.list_layout.insertWidget(self.list_layout.count() - 1, row)

    def _update_count(self) -> None:
        # 위젯 수명(deleteLater는 지연 삭제라 세는 시점이 애매하다)을 세는 대신
        # 저장소를 다시 센다. 삭제는 deleted 시그널 전에 이미 커밋돼 있다.
        self.ui.count_label.setText(f"{len(self.repository.list())}개")

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
