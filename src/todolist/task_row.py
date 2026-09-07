from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QStackedWidget,
    QWidget,
)

from todolist.models import Task
from todolist.repository import TaskRepository


class _ClickableLabel(QLabel):
    clicked = Signal()

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


class TaskRow(QWidget):
    def __init__(self, task: Task, repository: TaskRepository, parent: QWidget | None = None):
        super().__init__(parent)
        self.task = task
        self.repository = repository

        self.checkbox = QCheckBox()
        self.checkbox.setChecked(task.done)
        self.checkbox.stateChanged.connect(self._on_toggle_done)

        self.label = _ClickableLabel(task.text)
        self.label.clicked.connect(self._start_edit)

        self.edit = QLineEdit(task.text)
        self.edit.returnPressed.connect(self._finish_edit)
        self.edit.editingFinished.connect(self._finish_edit)

        self.text_stack = QStackedWidget()
        self.text_stack.addWidget(self.label)
        self.text_stack.addWidget(self.edit)

        self.delete_button = QPushButton("×")
        self.delete_button.setFixedWidth(24)
        self.delete_button.clicked.connect(self._on_delete)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.addWidget(self.checkbox)
        layout.addWidget(self.text_stack, 1)
        layout.addWidget(self.delete_button)

        self._apply_done_style()

    def _on_toggle_done(self) -> None:
        self.task = self.repository.update(self.task.id, done=self.checkbox.isChecked())
        self._apply_done_style()

    def _apply_done_style(self) -> None:
        font = self.label.font()
        font.setStrikeOut(self.task.done)
        self.label.setFont(font)

    def _start_edit(self) -> None:
        self.edit.setText(self.task.text)
        self.text_stack.setCurrentWidget(self.edit)
        self.edit.setFocus()
        self.edit.selectAll()

    def _finish_edit(self) -> None:
        if self.text_stack.currentWidget() is not self.edit:
            return
        new_text = self.edit.text().strip()
        if new_text and new_text != self.task.text:
            self.task = self.repository.update(self.task.id, text=new_text)
            self.label.setText(self.task.text)
        self.text_stack.setCurrentWidget(self.label)

    def _on_delete(self) -> None:
        self.repository.delete(self.task.id)
        self.deleteLater()
