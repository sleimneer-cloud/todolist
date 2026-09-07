import sys

from PySide6.QtWidgets import QApplication

from todolist.repository import LocalSqliteRepository
from todolist.window import TodoWindow


def main() -> None:
    app = QApplication(sys.argv)
    repository = LocalSqliteRepository()
    window = TodoWindow(repository)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
