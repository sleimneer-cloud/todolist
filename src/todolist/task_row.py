from datetime import date

from PySide6.QtCore import QDate, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QDateEdit,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QStackedWidget,
    QWidget,
)

from todolist.models import Task
from todolist.repository import TaskRepository
from todolist.urgency import urgency_color


class _ClickableLabel(QLabel):
    clicked = Signal()

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


class TaskRow(QWidget):
    def __init__(
        self, task: Task, repository: TaskRepository, parent: QWidget | None = None
    ):
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

        self.due_checkbox = QCheckBox("마감일")
        self.due_edit = QDateEdit(QDate.currentDate())
        self.due_edit.setCalendarPopup(True)
        self.due_checkbox.toggled.connect(self.due_edit.setEnabled)

        self.edit_container = QWidget()
        edit_layout = QHBoxLayout(self.edit_container)
        edit_layout.setContentsMargins(0, 0, 0, 0)
        edit_layout.addWidget(self.edit, 1)
        edit_layout.addWidget(self.due_checkbox)
        edit_layout.addWidget(self.due_edit)

        self.text_stack = QStackedWidget()
        self.text_stack.addWidget(self.label)
        self.text_stack.addWidget(self.edit_container)

        self.delete_button = QPushButton("×")
        self.delete_button.setFixedWidth(24)
        self.delete_button.clicked.connect(self._on_delete)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.addWidget(self.checkbox)
        layout.addWidget(self.text_stack, 1)
        layout.addWidget(self.delete_button)

        self._apply_style()

    def _on_toggle_done(self) -> None:
        self.task = self.repository.update(self.task.id, done=self.checkbox.isChecked())
        self._apply_style()

    def _apply_style(self) -> None:
        font = self.label.font()
        font.setStrikeOut(self.task.done)
        self.label.setFont(font)
        color = urgency_color(self.task.due_date, date.today())
        self.label.setStyleSheet(f"color: {color};")

    def _start_edit(self) -> None:
        self.edit.setText(self.task.text)
        self.due_checkbox.setChecked(self.task.due_date is not None)
        self.due_edit.setDate(QDate(self.task.due_date or date.today()))
        self.due_edit.setEnabled(self.due_checkbox.isChecked())
        self.text_stack.setCurrentWidget(self.edit_container)
        self.edit.setFocus()
        self.edit.selectAll()

    def _finish_edit(self) -> None:
        if self.text_stack.currentWidget() is not self.edit_container:
            return
        new_text = self.edit.text().strip() or self.task.text
        new_due_date = (
            self.due_edit.date().toPython() if self.due_checkbox.isChecked() else None
        )
        self.task = self.repository.update(
            self.task.id, text=new_text, due_date=new_due_date
        )
        self.label.setText(self.task.text)
        self._apply_style()
        self.text_stack.setCurrentWidget(self.label)

    def _on_delete(self) -> None:
        self.repository.delete(self.task.id)
        self.deleteLater()
