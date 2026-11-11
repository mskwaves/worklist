import sys
import os

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLineEdit, QPushButton, QListWidget, \
    QMessageBox, QFileDialog, QComboBox, QHBoxLayout, QLabel
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QTimer
from edit_dialog import EditDialog

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS  # Папка, куда EXE распаковывает файлы
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

os.chdir(base_path)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.is_dark_theme = True
        self.time_left = 1 * 60
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer_label = QLabel("1:00", self)

        self.setWindowTitle("WorkList")
        self.setWindowIcon(QIcon("icons/to-do-list_light.png"))
        self.setGeometry(400, 400, 400, 400)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.theme_button = QPushButton("Сменить тему", self)
        self.focus_button = QPushButton("Фокус", self)
        self.theme_button.setFixedWidth(100)
        self.input_field = QLineEdit(self)
        self.add_button = QPushButton("\tДобавить", self)
        self.task_list = QListWidget(self)
        self.delete_task = QPushButton("\tУдалить")
        self.save_csv = QPushButton("\tСохранить в CSV", self)
        self.open_csv = QPushButton("\tЗагрузить CSV", self)
        self.priority_box = QComboBox(self)
        self.priority_box.addItems(["Обычный", "Важный", "Срочный"])

        layout = QVBoxLayout(central_widget)
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.theme_button)
        top_layout.addWidget(self.focus_button)
        top_layout.addWidget(self.timer_label)
        layout.addLayout(top_layout)
        layout.addWidget(self.input_field)
        layout.addWidget(self.add_button)
        layout.addWidget(self.task_list)
        layout.addWidget(self.delete_task)
        layout.addWidget(self.save_csv)
        layout.addWidget(self.open_csv)
        layout.addWidget(self.priority_box)

        self.add_button.clicked.connect(self.add_task)
        self.delete_task.clicked.connect(self.delete_task_action)
        self.save_csv.clicked.connect(self.save_csv_action)
        self.open_csv.clicked.connect(self.open_csv_action)
        self.task_list.itemDoubleClicked.connect(self.edit_task_action)
        self.theme_button.clicked.connect(self.toggle_theme)
        self.focus_button.clicked.connect(self.focus_mode)

        self.setStyleSheet(self.load_qss("styles/dark.qss"))
        self.timer_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.update_icons()

    def add_task(self):
        text = self.input_field.text()
        if not text:
            return
        priority = self.priority_box.currentText()
        full_text = f"[{priority}] {text}"
        self.task_list.addItem(full_text)
        self.input_field.clear()

    def delete_task_action(self):
        item = self.task_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Ошибка", "Выберите задачу для удаления")
            return
        text = item.text()
        reply = QMessageBox.question(
            self,
            "Удаление",
            f"Удалить задачу '{text}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No  # Кнопка по умолчанию - "Нет"
        )
        if reply == QMessageBox.StandardButton.Yes:
            row = self.task_list.row(item)
            self.task_list.takeItem(row)

    def save_csv_action(self):
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить задачи", f"tasks.csv", "CSV (*.csv)")
        if not path:
            return
        try:
            with open(path, "w", encoding='utf-8', newline="") as f:
                for i in range(self.task_list.count()):
                    text = self.task_list.item(i).text()
                    f.write(text + "\n")
        except OSError as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить: {e}")
            return
        QMessageBox.information(self, "Готово", f"Сохранено {self.task_list.count()} задач")

    def open_csv_action(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Открыть текст", "", "CSV (*.csv);;All Files (*)")
        if not file_name:
            return
        try:  # Если выбрали файл
            with open(file_name, 'r', encoding='utf-8') as file:  # 'r' — read, как чтение книги
                lines = file.readlines()
        except OSError as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось прочитать: {e}")
            return
        for line in lines:
            line = line.strip()
            if line:
                self.task_list.addItem(line)
        QMessageBox.information(self, "Готово", f"Загружено {len(lines)} задач")

    def edit_task_action(self, item):
        current_text = item.text()
        dialog = EditDialog(current_text, self)
        if dialog.exec():
            new_text = dialog.get_text()
            item.setText(new_text)

    def load_qss(self, filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        except OSError as e:
            print(f"Ошибка загрузки стилей: {e}")
            return ""

    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        if self.is_dark_theme:
            self.setStyleSheet(self.load_qss("styles/dark.qss"))
        else:
            self.setStyleSheet(self.load_qss("styles/light.qss"))
        self.update_icons()

    def update_icons(self):
        theme = "dark" if self.is_dark_theme else "light"

        self.add_button.setIcon(QIcon(f"icons/add_{theme}.png"))
        self.delete_task.setIcon(QIcon(f"icons/delete_{theme}.png"))
        self.save_csv.setIcon(QIcon(f"icons/save_{theme}.png"))
        self.open_csv.setIcon(QIcon(f"icons/open_{theme}.png"))
        self.setWindowIcon(QIcon(f"icons/to-do-list_{theme}.png"))

    def focus_mode(self):
        if not self.task_list.currentItem():
            QMessageBox.warning(self, "Ошибка", "Выберите задачу для фокуса!")
            return

        if self.timer.isActive():
            self.timer.stop()
            self.timer_label.setText("1:00")
            self.focus_button.setText("Фокус")
            self.add_button.setEnabled(True)
            self.delete_task.setEnabled(True)
            self.save_csv.setEnabled(True)
            self.open_csv.setEnabled(True)
            return

        self.add_button.setEnabled(False)
        self.delete_task.setEnabled(False)
        self.save_csv.setEnabled(False)
        self.open_csv.setEnabled(False)

        self.focus_button.setText("Стоп")
        self.time_left = 1 * 60
        self.timer.start(1000)

    def update_timer(self):
        self.time_left -= 1
        minutes = self.time_left // 60
        seconds = self.time_left % 60
        self.timer_label.setText(f"{minutes:02d}:{seconds:02d}")

        if self.time_left <= 0:
            self.timer.stop()

            self.focus_button.setText("Фокус")
            self.timer_label.setText("30:00")

            self.add_button.setEnabled(True)
            self.delete_task.setEnabled(True)
            self.save_csv.setEnabled(True)
            self.open_csv.setEnabled(True)
            QMessageBox.information(self, "Молодец!", "Время вышло! Можешь отдохнуть")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
