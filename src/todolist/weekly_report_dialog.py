from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class WeeklyReportDialog(QDialog):
    """생성된 주간 업무일지를 보여주는 다이얼로그. 복사 버튼 + 텍스트 선택 모두 지원."""

    def __init__(self, report_text: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("주간 업무일지")
        self.resize(360, 280)

        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(report_text)
        self.text_edit.setReadOnly(True)

        copy_button = QPushButton("복사")
        copy_button.clicked.connect(self._copy_to_clipboard)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.close)

        button_row = QHBoxLayout()
        button_row.addWidget(copy_button)
        button_row.addWidget(buttons)

        layout = QVBoxLayout(self)
        layout.addWidget(self.text_edit)
        layout.addLayout(button_row)

    def _copy_to_clipboard(self) -> None:
        QApplication.clipboard().setText(self.text_edit.toPlainText())
