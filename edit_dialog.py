from PyQt6.QtWidgets import QDialog, QLineEdit, QPushButton, QVBoxLayout


class EditDialog(QDialog):
    def __init__(self, current_text, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактировать задачу")

        self.input_text = QLineEdit()
        self.input_text.setText(current_text)

        self.save_button = QPushButton("Сохранить")
        self.cancel_button = QPushButton("Отмена")

        layout = QVBoxLayout()
        layout.addWidget(self.input_text)
        layout.addWidget(self.save_button)
        layout.addWidget(self.cancel_button)

        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        self.setLayout(layout)

    def get_text(self):
        return self.input_text.text()

