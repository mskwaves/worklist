from PyQt6.QtWidgets import (
    QDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
)

import db


class ArchiveWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Архив")
        self.resize(520, 540)

        self.title_label = QLabel("Выполненные задачи", self)
        self.archive_list = QListWidget(self)
        self.close_button = QPushButton("Закрыть", self)

        layout = QVBoxLayout(self)
        layout.addWidget(self.title_label)
        layout.addWidget(self.archive_list)
        layout.addWidget(self.close_button)

        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.close_button.clicked.connect(self.accept)
        self.load_archive()

    def load_archive(self):
        rows = db.load_archive()
        self.title_label.setText(f"Выполненные задачи — {len(rows)}")
        for row in rows:
            text = f"{row['archived_at']} · [{row['priority']}] {row['text']}"
            self.archive_list.addItem(QListWidgetItem(text))
        if not rows:
            self.archive_list.addItem(QListWidgetItem("Архив пуст"))
