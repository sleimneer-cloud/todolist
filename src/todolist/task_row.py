from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

from todolist.models import Task


class TaskRow(QWidget):
    def __init__(self, task: Task, parent: QWidget | None = None):
        super().__init__(parent)
        self.task = task
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        self.label = QLabel(task.text)
        layout.addWidget(self.label)
