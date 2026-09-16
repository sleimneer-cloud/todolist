# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'add_task_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDateEdit, QDateTimeEdit,
    QDialog, QDialogButtonBox, QFormLayout, QLabel,
    QLineEdit, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(360, 240)
        Dialog.setMinimumSize(QSize(340, 220))
        self.root_layout = QVBoxLayout(Dialog)
        self.root_layout.setSpacing(14)
        self.root_layout.setObjectName(u"root_layout")
        self.root_layout.setContentsMargins(20, 18, 20, 16)
        self.add_title_label = QLabel(Dialog)
        self.add_title_label.setObjectName(u"add_title_label")

        self.root_layout.addWidget(self.add_title_label)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setHorizontalSpacing(12)
        self.formLayout.setVerticalSpacing(10)
        self.formLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.add_task_label = QLabel(Dialog)
        self.add_task_label.setObjectName(u"add_task_label")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.add_task_label)

        self.add_task_edit = QLineEdit(Dialog)
        self.add_task_edit.setObjectName(u"add_task_edit")
        self.add_task_edit.setClearButtonEnabled(True)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.add_task_edit)

        self.add_start_date_label = QLabel(Dialog)
        self.add_start_date_label.setObjectName(u"add_start_date_label")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.add_start_date_label)

        self.add_start_dateEdit = QDateEdit(Dialog)
        self.add_start_dateEdit.setObjectName(u"add_start_dateEdit")
        self.add_start_dateEdit.setCalendarPopup(True)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.add_start_dateEdit)

        self.add_end_date_label = QLabel(Dialog)
        self.add_end_date_label.setObjectName(u"add_end_date_label")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.add_end_date_label)

        self.add_end_dateEdit = QDateTimeEdit(Dialog)
        self.add_end_dateEdit.setObjectName(u"add_end_dateEdit")
        self.add_end_dateEdit.setCalendarPopup(True)

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.add_end_dateEdit)


        self.root_layout.addLayout(self.formLayout)

        self.form_spacer = QSpacerItem(20, 8, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.root_layout.addItem(self.form_spacer)

        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.root_layout.addWidget(self.buttonBox)


        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"\uc77c\uc815 \ucd94\uac00", None))
        self.add_title_label.setText(QCoreApplication.translate("Dialog", u"\uc77c\uc815 \ucd94\uac00", None))
        self.add_task_label.setText(QCoreApplication.translate("Dialog", u"\ud560 \uc77c", None))
        self.add_task_edit.setPlaceholderText(QCoreApplication.translate("Dialog", u"\ubb34\uc5c7\uc744 \ud574\uc57c \ud558\ub098\uc694?", None))
        self.add_start_date_label.setText(QCoreApplication.translate("Dialog", u"\uc2dc\uc791\uc77c", None))
        self.add_start_dateEdit.setDisplayFormat(QCoreApplication.translate("Dialog", u"yyyy-MM-dd", None))
        self.add_end_date_label.setText(QCoreApplication.translate("Dialog", u"\ub9c8\uac10\uc77c\uc2dc", None))
        self.add_end_dateEdit.setDisplayFormat(QCoreApplication.translate("Dialog", u"yyyy-MM-dd HH:mm", None))
    # retranslateUi

