from datetime import date

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QDialog, QWidget

from todolist.ui_add_task_dialog import Ui_Dialog


class AddTaskDialog(QDialog):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        today = QDate.currentDate()
        self.ui.add_start_dateEdit.setDate(today)
        self.ui.add_end_dateEdit.setDate(today)

    def values(self) -> tuple[str, date, date]:
        text = self.ui.add_task_edit.text().strip()
        start_date = self.ui.add_start_dateEdit.date().toPython()
        due_date = self.ui.add_end_dateEdit.date().toPython()
        return text, start_date, due_date
