from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QLineEdit, QVBoxLayout, QWidget

from todolist.geometry import compute_bottom_right_position
from todolist.repository import TaskRepository
from todolist.task_row import TaskRow

WINDOW_WIDTH = 300
WINDOW_HEIGHT = 420
SCREEN_MARGIN = 16


class TodoWindow(QWidget):
    def __init__(self, repository: TaskRepository, parent: QWidget | None = None):
        super().__init__(parent)
        self.repository = repository

        # Qt.Tool keeps the widget out of the dock/Cmd-Tab switcher, matching
        # a persistent desktop widget rather than a regular application window.
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)

        self.input = QLineEdit()
        self.input.setPlaceholderText("할 일 추가...")
        self.input.returnPressed.connect(self._on_add_task)

        self.list_layout = QVBoxLayout()
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.addStretch()

        layout = QVBoxLayout(self)
        layout.addWidget(self.input)
        layout.addLayout(self.list_layout)

        self._load_tasks()
        self._position_bottom_right()

    def _load_tasks(self) -> None:
        for task in self.repository.list():
            self._add_row(task)

    def _add_row(self, task) -> None:
        row = TaskRow(task)
        self.list_layout.insertWidget(self.list_layout.count() - 1, row)

    def _on_add_task(self) -> None:
        text = self.input.text().strip()
        if not text:
            return
        task = self.repository.add(text, due_date=None)
        self._add_row(task)
        self.input.clear()

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
