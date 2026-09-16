from datetime import date

from PySide6.QtCore import QDateTime, Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QDateTimeEdit,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QWidget,
)

from todolist.data.models import Task
from todolist.data.repository import TaskRepository
from todolist.logic.due_format import format_due
from todolist.logic.urgency import urgency_color

ROW_HEIGHT = 30
URGENCY_BAR_WIDTH = 3


class _ClickableLabel(QLabel):
    clicked = Signal()

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


class TaskRow(QWidget):
    # 창이 남은 개수를 다시 셀 수 있게 알린다. destroyed를 쓰면 이미 파괴 중이라
    # 남은 행을 세는 시점이 애매해진다.
    deleted = Signal()

    def __init__(
        self, task: Task, repository: TaskRepository, parent: QWidget | None = None
    ):
        super().__init__(parent)
        self.task = task
        self.repository = repository
        self.setObjectName("taskRow")

        # 행이 sizeHint(30px)를 넘어 늘어나지 않게 고정한다. Preferred는 남는
        # 세로 공간을 같이 나눠 가져서 행이 77px까지 부풀었다.
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(ROW_HEIGHT)

        self.urgency_bar = QFrame()
        self.urgency_bar.setObjectName("urgencyBar")
        self.urgency_bar.setFixedWidth(URGENCY_BAR_WIDTH)

        self.checkbox = QCheckBox()
        # setChecked를 connect보다 먼저 — 순서가 바뀌면 복원하는 순간
        # stateChanged가 발화해 방금 불러온 항목이 삭제된다.
        self.checkbox.setChecked(task.done)
        self.checkbox.stateChanged.connect(self._on_toggle_done)

        self.label = _ClickableLabel(task.text)
        self.label.setObjectName("taskLabel")
        self.label.setCursor(Qt.CursorShape.IBeamCursor)
        self.label.clicked.connect(self._start_edit)

        self.due_label = QLabel()
        self.due_label.setObjectName("dueLabel")
        self.due_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        self.edit = QLineEdit(task.text)
        self.edit.returnPressed.connect(self._finish_edit)
        self.edit.editingFinished.connect(self._finish_edit)

        self.due_checkbox = QCheckBox("마감일")
        self.due_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self.due_edit.setCalendarPopup(True)
        self.due_edit.setDisplayFormat("MM-dd HH:mm")
        self.due_checkbox.toggled.connect(self.due_edit.setEnabled)

        self.edit_container = QWidget()
        edit_layout = QHBoxLayout(self.edit_container)
        edit_layout.setContentsMargins(0, 0, 0, 0)
        edit_layout.setSpacing(6)
        edit_layout.addWidget(self.edit, 1)
        edit_layout.addWidget(self.due_checkbox)
        edit_layout.addWidget(self.due_edit)

        # 읽기 모드(라벨+마감일)와 수정 모드를 같은 자리에서 갈아끼운다.
        self.read_container = QWidget()
        read_layout = QHBoxLayout(self.read_container)
        read_layout.setContentsMargins(0, 0, 0, 0)
        read_layout.setSpacing(8)
        read_layout.addWidget(self.label, 1)
        read_layout.addWidget(self.due_label)

        self.text_stack = QStackedWidget()
        self.text_stack.addWidget(self.read_container)
        self.text_stack.addWidget(self.edit_container)

        self.delete_button = QPushButton("×")
        self.delete_button.setObjectName("deleteButton")
        self.delete_button.setFixedSize(18, 18)
        self.delete_button.setFlat(True)
        self.delete_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_button.clicked.connect(self._on_delete)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(9)
        layout.addWidget(self.urgency_bar)
        layout.addWidget(self.checkbox)
        layout.addWidget(self.text_stack, 1)
        layout.addWidget(self.delete_button)

        self._apply_style()

    def _on_toggle_done(self) -> None:
        if self.checkbox.isChecked():
            # DB에서 지우지 않는다 — row는 완료 상태로 남겨야 주간 업무일지가
            # (list_for_week로) 이번 주에 완료한 일까지 요약에 포함시킬 수
            # 있다. deleted 시그널은 "목록 창에서 사라졌다"는 뜻이지 DB
            # 삭제를 의미하지 않는다 (× 버튼 쪽만 진짜로 delete()한다).
            self.repository.update(self.task.id, done=True)
            self.deleted.emit()
            self.deleteLater()

    def _apply_style(self) -> None:
        font = self.label.font()
        font.setStrikeOut(self.task.done)
        self.label.setFont(font)

        due = self.task.due_date.date() if self.task.due_date else None
        color = urgency_color(due, date.today())
        # 색은 좌측 바와 마감일 텍스트만 쓰고, 본문은 QSS의 기본 전경색을
        # 유지한다. 빨간 본문은 읽기 어렵고 목록 전체가 경고처럼 보인다.
        self.urgency_bar.setStyleSheet(
            f"#urgencyBar {{ background-color: {color}; border-radius: 1px; }}"
        )
        self.due_label.setStyleSheet(f"#dueLabel {{ color: {color}; }}")
        self.due_label.setText(format_due(self.task.due_date))

    def _start_edit(self) -> None:
        self.edit.setText(self.task.text)
        self.due_checkbox.setChecked(self.task.due_date is not None)
        self.due_edit.setDateTime(
            QDateTime(self.task.due_date) if self.task.due_date else QDateTime.currentDateTime()
        )
        self.due_edit.setEnabled(self.due_checkbox.isChecked())
        self.text_stack.setCurrentWidget(self.edit_container)
        self.edit.setFocus()
        self.edit.selectAll()

    def _finish_edit(self) -> None:
        if self.text_stack.currentWidget() is not self.edit_container:
            return
        new_text = self.edit.text().strip() or self.task.text
        new_due_date = (
            self.due_edit.dateTime().toPython() if self.due_checkbox.isChecked() else None
        )
        self.task = self.repository.update(
            self.task.id, text=new_text, due_date=new_due_date
        )
        self.label.setText(self.task.text)
        self._apply_style()
        self.text_stack.setCurrentWidget(self.read_container)

    def _on_delete(self) -> None:
        self.repository.delete(self.task.id)
        self.deleted.emit()
        self.deleteLater()
