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

        self.list_layout = QVBoxLayout(self.ui.scrollAreaWidgetContents)
        self.list_layout.addStretch()

        self.ui.add_todo_button.clicked.connect(self._on_add_task)

        self._load_tasks()
        self._position_bottom_right()

    def _load_tasks(self) -> None:
        for task in self.repository.list():
            self._add_row(task)

    def _add_row(self, task) -> None:
        row = TaskRow(task, self.repository)
        self.list_layout.insertWidget(self.list_layout.count() - 1, row)

    def _on_add_task(self) -> None:
        dialog = AddTaskDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        text, start_date, due_date = dialog.values()
        if not text:
            return
        task = self.repository.add(text, due_date=due_date, start_date=start_date)
        self._add_row(task)

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
