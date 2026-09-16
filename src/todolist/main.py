import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from todolist.repository import LocalSqliteRepository
from todolist.window import TodoWindow

STYLE_PATH = Path(__file__).with_name("style.qss")


def load_stylesheet() -> str:
    # 스타일이 없어도 앱은 떠야 한다 — PyInstaller 번들에서 데이터 파일이
    # 빠졌을 때 앱이 죽는 대신 기본 위젯 모양으로 뜨게 한다.
    try:
        return STYLE_PATH.read_text(encoding="utf-8")
    except OSError:
        return ""


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyleSheet(load_stylesheet())
    repository = LocalSqliteRepository()
    window = TodoWindow(repository)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
