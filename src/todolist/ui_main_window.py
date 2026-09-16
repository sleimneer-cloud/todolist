# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QFrame, QHBoxLayout,
    QLabel, QPushButton, QScrollArea, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(320, 420)
        Dialog.setMinimumSize(QSize(300, 360))
        self.root_layout = QVBoxLayout(Dialog)
        self.root_layout.setSpacing(10)
        self.root_layout.setObjectName(u"root_layout")
        self.root_layout.setContentsMargins(14, 12, 14, 12)
        self.header_layout = QHBoxLayout()
        self.header_layout.setSpacing(8)
        self.header_layout.setObjectName(u"header_layout")
        self.title_label = QLabel(Dialog)
        self.title_label.setObjectName(u"title_label")

        self.header_layout.addWidget(self.title_label)

        self.count_label = QLabel(Dialog)
        self.count_label.setObjectName(u"count_label")

        self.header_layout.addWidget(self.count_label)

        self.header_spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.header_layout.addItem(self.header_spacer)


        self.root_layout.addLayout(self.header_layout)

        self.scrollArea = QScrollArea(Dialog)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 292, 340))
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.root_layout.addWidget(self.scrollArea)

        self.add_todo_button = QPushButton(Dialog)
        self.add_todo_button.setObjectName(u"add_todo_button")
        self.add_todo_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.add_todo_button.setFlat(True)

        self.root_layout.addWidget(self.add_todo_button)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"todolist", None))
        self.title_label.setText(QCoreApplication.translate("Dialog", u"\ud560 \uc77c", None))
        self.count_label.setText(QCoreApplication.translate("Dialog", u"0\uac1c", None))
        self.add_todo_button.setText(QCoreApplication.translate("Dialog", u"\uff0b  \uc77c\uc815 \ucd94\uac00", None))
    # retranslateUi

