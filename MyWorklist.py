import sys
import os
import db

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLineEdit, QPushButton, QListWidget, \
    QMessageBox, QFileDialog, QComboBox, QHBoxLayout, QLabel, QListWidgetItem
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QTimer, Qt
from edit_dialog import EditDialog
from archive_window import ArchiveWindow

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
        self.timer_label = QLabel("30:00", self)

        self.setWindowTitle("WorkList")
        self.setWindowIcon(QIcon("icons/to-do-list_light.png"))
        self.setGeometry(400, 300, 480, 620)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.theme_button = QPushButton("Сменить тему", self)
        self.focus_button = QPushButton("Фокус", self)
        self.theme_button.setFixedWidth(100)
        self.input_field = QLineEdit(self)
        self.search_field = QLineEdit(self)
        self.search_field.setPlaceholderText("Поиск задач...")
        self.add_button = QPushButton("\tДобавить", self)
        self.task_list = QListWidget(self)
        self.delete_task = QPushButton("\tУдалить")
        self.complete_task = QPushButton("\tВыполнено", self)
        self.archive_button = QPushButton("\tАрхив", self)
        self.save_csv = QPushButton("\tСохранить в CSV", self)
        self.open_file = QPushButton("\tЗагрузить файл", self)
        self.priority_box = QComboBox(self)
        self.priority_box.addItems(["Обычный", "Важный", "Срочный"])

        layout = QVBoxLayout(central_widget)
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.theme_button)
        top_layout.addWidget(self.focus_button)
        top_layout.addWidget(self.timer_label)
        layout.addLayout(top_layout)
        layout.addWidget(self.input_field)
        layout.addWidget(self.search_field)
        layout.addWidget(self.add_button)
        layout.addWidget(self.task_list)
        layout.addWidget(self.delete_task)
        layout.addWidget(self.complete_task)
        layout.addWidget(self.archive_button)
        layout.addWidget(self.save_csv)
        layout.addWidget(self.open_file)
        layout.addWidget(self.priority_box)

        self.add_button.clicked.connect(self.add_task)
        self.delete_task.clicked.connect(self.delete_task_action)
        self.complete_task.clicked.connect(self.complete_task_action)
        self.archive_button.clicked.connect(self.open_archive)
        self.save_csv.clicked.connect(self.save_csv_action)
        self.open_file.clicked.connect(self.open_file_action)
        self.task_list.itemDoubleClicked.connect(self.edit_task_action)
        self.theme_button.clicked.connect(self.toggle_theme)
        self.focus_button.clicked.connect(self.focus_mode)
        self.search_field.textChanged.connect(self.filter_tasks)

        self.setStyleSheet(self.load_qss("styles/dark.qss"))
        self.timer_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.update_icons()
        self.load_tasks_from_db()

    def add_row_to_list(self, row):
        item = QListWidgetItem(f"[{row['priority']}] {row['text']}")
        item.setData(Qt.ItemDataRole.UserRole, row["id"])
        item.setData(Qt.ItemDataRole.UserRole + 1, row["priority"])
        item.setData(Qt.ItemDataRole.UserRole + 2, row["text"])
        self.task_list.addItem(item)

    def load_tasks_from_db(self):
        for row in db.load_tasks():
            self.add_row_to_list(row)

    def filter_tasks(self):
        query = self.search_field.text().strip()
        self.task_list.clear()
        for row in db.search_tasks(query):
            self.add_row_to_list(row)

    def add_task(self):
        text = self.input_field.text()
        if not text:
            return
        priority = self.priority_box.currentText()
        task_id = db.add_task(text, priority)
        item = QListWidgetItem(f"[{priority}] {text}")
        item.setData(Qt.ItemDataRole.UserRole, task_id)
        item.setData(Qt.ItemDataRole.UserRole + 1, priority)
        item.setData(Qt.ItemDataRole.UserRole + 2, text)
        self.task_list.addItem(item)
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
            task_id = item.data(Qt.ItemDataRole.UserRole)
            db.delete_task(task_id)
            row = self.task_list.row(item)
            self.task_list.takeItem(row)

    def complete_task_action(self):
        item = self.task_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Ошибка", "Выберите задачу, чтобы отметить выполненной")
            return
        task_id = item.data(Qt.ItemDataRole.UserRole)
        if db.archive_task(task_id):
            self.task_list.takeItem(self.task_list.row(item))

    def open_archive(self):
        window = ArchiveWindow(self)
        window.exec()

    def save_csv_action(self):
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить задачи", f"tasks.csv", "CSV (*.csv)")
        if not path:
            return
        try:
            with open(path, "w", encoding='utf-8', newline="") as f:
                for i in range(self.task_list.count()):
                    item = self.task_list.item(i)
                    text = item.data(Qt.ItemDataRole.UserRole + 2) or item.text()
                    f.write(text + "\n")
        except OSError as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить: {e}")
            return
        QMessageBox.information(self, "Готово", f"Сохранено {self.task_list.count()} задач")

    def open_file_action(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Открыть файл", "", "CSV и TXT (*.csv *.txt)")
        if not file_name:
           return
        ext = os.path.splitext(file_name)[1].lower()
        if ext not in (".csv", ".txt"):
           QMessageBox.warning(self, "Ошибка", "Можно открыть только файл CSV или TXT!")
           return
        try:  # Если выбрали файл
            with open(file_name, 'r', encoding='utf-8') as file:  # 'r' — read, как чтение книги
                lines = file.readlines()
        except OSError as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось прочитать: {e}")
            return
        added = 0
        for line in lines:
            line = line.strip()
            if line:
                task_id = db.add_task(line, "Обычный")
                item = QListWidgetItem(f"[Обычный] {line}")
                item.setData(Qt.ItemDataRole.UserRole, task_id)
                item.setData(Qt.ItemDataRole.UserRole + 1, "Обычный")
                item.setData(Qt.ItemDataRole.UserRole + 2, line)
                self.task_list.addItem(item)
                added += 1
        QMessageBox.information(self, "Готово", f"Загружено {added} задач")

    def edit_task_action(self, item):
        current_text = item.data(Qt.ItemDataRole.UserRole + 2) or item.text()
        dialog = EditDialog(current_text, self)
        if dialog.exec():
            new_text = dialog.get_text().strip()
            if not new_text:
                return
            task_id = item.data(Qt.ItemDataRole.UserRole)
            priority = item.data(Qt.ItemDataRole.UserRole + 1)
            db.update_task(task_id, new_text, priority)
            item.setText(f"[{priority}] {new_text}")
            item.setData(Qt.ItemDataRole.UserRole + 2, new_text)

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
        self.complete_task.setIcon(QIcon(f"icons/check_{theme}.png"))
        self.archive_button.setIcon(QIcon(f"icons/archive_{theme}.png"))
        self.save_csv.setIcon(QIcon(f"icons/save_{theme}.png"))
        self.open_file.setIcon(QIcon(f"icons/open_{theme}.png"))
        self.setWindowIcon(QIcon(f"icons/to-do-list_{theme}.png"))

    def focus_mode(self):
        if not self.task_list.currentItem():
            QMessageBox.warning(self, "Ошибка", "Выберите задачу для фокуса!")
            return

        if self.timer.isActive():
            self.timer.stop()
            self.timer_label.setText("30:00")
            self.focus_button.setText("Фокус")
            self.add_button.setEnabled(True)
            self.delete_task.setEnabled(True)
            self.complete_task.setEnabled(True)
            self.archive_button.setEnabled(True)
            self.save_csv.setEnabled(True)
            self.open_file.setEnabled(True)
            return

        self.add_button.setEnabled(False)
        self.delete_task.setEnabled(False)
        self.complete_task.setEnabled(False)
        self.archive_button.setEnabled(False)
        self.save_csv.setEnabled(False)
        self.open_file.setEnabled(False)

        self.focus_button.setText("Стоп")
        self.time_left = 30 * 60
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
            self.complete_task.setEnabled(True)
            self.archive_button.setEnabled(True)
            self.save_csv.setEnabled(True)
            self.open_file.setEnabled(True)
            QMessageBox.information(self, "Молодец!", "Время вышло! Можешь отдохнуть")


if __name__ == '__main__':
    db.init_db()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
