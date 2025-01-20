from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QLineEdit, QMessageBox, QWidget, QMenuBar, QInputDialog
from PySide6.QtGui import QIcon, QAction, QPixmap, QPainter, QBrush
from PySide6.QtCore import Qt
import re
import os  
from datetime import datetime
import platform


# Функция для изменения даты
def change_file_dates(file_path, creation_date, modification_date):
    try:
        # Преобразование дат в формат timestamp
        mod_time = datetime.strptime(modification_date, "%Y-%m-%d %H:%M:%S").timestamp()
        
        if platform.system() == "Windows":
            # Для Windows используем ctypes для изменения даты создания
            import ctypes
            creation_time = datetime.strptime(creation_date, "%Y-%m-%d %H:%M:%S").timestamp()
            
            # Преобразование времени в формат Windows FILETIME
            ctime = int(creation_time * 10000000 + 116444736000000000)
            mtime = int(mod_time * 10000000 + 116444736000000000)
            
            # Изменяем атрибуты файла
            handle = ctypes.windll.kernel32.CreateFileW(
                file_path, 256, 0, None, 3, 128, None
            )
            if handle == -1:
                raise Exception("Не удалось открыть файл для изменения.")

            ctime_ft = ctypes.c_longlong(ctime)
            mtime_ft = ctypes.c_longlong(mtime)

            ctypes.windll.kernel32.SetFileTime(
                handle, ctypes.byref(ctime_ft), None, ctypes.byref(mtime_ft)
            )
            ctypes.windll.kernel32.CloseHandle(handle)
        else:
            # Для Unix-подобных систем меняем только mtime (дата создания неизменна)
            os.utime(file_path, (mod_time, mod_time))

        QMessageBox.information(None, "Успех", "Даты успешно изменены!")
    except Exception as e:
        QMessageBox.critical(None, "Ошибка", f"Не удалось изменить даты: {e}")


# Окно для изменения даты файлов
class FileDateChanger(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("FileTime Change by yukimura")
        self.setGeometry(300, 300, 600, 300)
        self.setStyleSheet("background-color: #2e2e2e; color: white;")  # Dark background with white text

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        # Метка для отображения пути файла
        self.file_label = QLabel("Файл не выбран")
        self.file_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.file_label)

        # Кнопка для выбора файла
        select_button = QPushButton("Выбрать файл")
        select_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;  /* Green */
                border-radius: 10px;
                color: white;
                padding: 12px;
                font-size: 16px;
                transition: background-color 0.3s;
            }
            QPushButton:hover {
                background-color: #45a049;  /* Darker Green */
            }
        """)
        select_button.clicked.connect(self.select_file)
        layout.addWidget(select_button)

        # Поля для ввода дат
        self.creation_date_input = QLineEdit()
        self.creation_date_input.setPlaceholderText("Дата создания (YYYY-MM-DD HH:MM:SS)")
        self.creation_date_input.setStyleSheet("""
            QLineEdit {
                background-color: #333333;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
        """)
        layout.addWidget(self.creation_date_input)

        self.modification_date_input = QLineEdit()
        self.modification_date_input.setPlaceholderText("Дата последней модификации (YYYY-MM-DD HH:MM:SS)")
        self.modification_date_input.setStyleSheet("""
            QLineEdit {
                background-color: #333333;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
        """)
        layout.addWidget(self.modification_date_input)

        # Кнопка для применения изменений
        apply_button = QPushButton("Изменить даты")
        apply_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border-radius: 10px;
                color: white;
                padding: 12px;
                font-size: 16px;
                transition: background-color 0.3s;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        apply_button.clicked.connect(self.apply_changes)
        layout.addWidget(apply_button)

        central_widget.setLayout(layout)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл")
        if file_path:
            self.file_label.setText(file_path)
            self.file_label.file_path = file_path

    def apply_changes(self):
        file_path = getattr(self.file_label, 'file_path', None)
        if not file_path:
            QMessageBox.warning(self, "Предупреждение", "Выберите файл!")
            return

        creation_date = self.creation_date_input.text()
        modification_date = self.modification_date_input.text()

        if not creation_date or not modification_date:
            QMessageBox.warning(self, "Предупреждение", "Заполните обе даты!")
            return

        if not re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", creation_date):
            QMessageBox.warning(self, "Ошибка", "Неверный формат даты создания!")
            return

        if not re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", modification_date):
            QMessageBox.warning(self, "Ошибка", "Неверный формат даты модификации!")
            return

        change_file_dates(file_path, creation_date, modification_date)


# Главное приложение
class CiscoCleanerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cisco Packet Tracer Cleaner by yukimura")
        self.setGeometry(100, 100, 600, 400)
        self.setStyleSheet("background-color: #2e2e2e; color: white;")  # Dark background with white text
        self.background_image = None  # Placeholder for the background image
        self.initUI()

        # Set taskbar icon (small logo)
        self.setWindowIcon(QIcon('logo_small.ico'))  # Replace with your small logo file

    def initUI(self):
        # Main widget and layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Set background image
        self.set_background_image()

        # Menu bar
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        file_menu = menu_bar.addMenu("Файл")
        clean_action = QAction(QIcon(), "Очистить файл", self)
        clean_action.triggered.connect(self.clean_file)
        file_menu.addAction(clean_action)

        replace_action = QAction(QIcon(), "Заменить IP и очистить", self)
        replace_action.triggered.connect(self.replace_ips)
        file_menu.addAction(replace_action)

        replace_keep_action = QAction(QIcon(), "Заменить IP (сохранить '!')", self)
        replace_keep_action.triggered.connect(self.replace_ips_keep_exclamations)
        file_menu.addAction(replace_keep_action)

        file_menu.addSeparator()

        # New action for changing file dates
        change_dates_action = QAction("Изменить даты файла", self)
        change_dates_action.triggered.connect(self.change_file_dates)
        file_menu.addAction(change_dates_action)

        # New action for replacing password in a text file
        replace_password_action = QAction("Заменить пароль в файле", self)
        replace_password_action.triggered.connect(self.replace_password)
        file_menu.addAction(replace_password_action)

        # New action to open program folder
        open_folder_action = QAction("Открыть папку программы", self)
        open_folder_action.triggered.connect(self.open_program_folder)
        file_menu.addAction(open_folder_action)

        exit_action = QAction(QIcon(), "Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # About menu
        help_menu = menu_bar.addMenu("Справка")
        about_action = QAction("О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        # Program logo at the top-left corner
        self.logo_label = QLabel(self)
        self.logo_pixmap = QPixmap('logo.png')  # Replace with your logo file
        self.logo_pixmap = self.logo_pixmap.scaled(50, 50, Qt.KeepAspectRatio)  # Resize the logo
        self.logo_label.setPixmap(self.logo_pixmap)
        self.logo_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.main_layout.addWidget(self.logo_label)

        # Clean file section
        self.label_clean = QLabel("Очистка файла от строк с '!':", self)
        self.main_layout.addWidget(self.label_clean)

        self.button_clean = QPushButton("Выбрать файл и очистить", self)
        self.button_clean.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;  /* Green */
                border-radius: 10px;
                color: white;
                padding: 12px;
                font-size: 16px;
                transition: background-color 0.3s;
            }
            QPushButton:hover {
                background-color: #45a049;  /* Darker Green */
            }
        """)
        self.button_clean.clicked.connect(self.clean_file)
        self.main_layout.addWidget(self.button_clean)

        # Replace IP section
        self.label_replace = QLabel("Замена IP-адресов и очистка файла:", self)
        self.main_layout.addWidget(self.label_replace)

        self.replace_layout = QHBoxLayout()
        self.replace_label = QLabel("Третий октет:")
        self.replace_input = QLineEdit(self)
        self.replace_input.setStyleSheet("""
            QLineEdit {
                background-color: #333333;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
        """)
        self.replace_button = QPushButton("Выбрать файл и заменить", self)
        self.replace_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border-radius: 10px;
                color: white;
                padding: 12px;
                font-size: 16px;
                transition: background-color 0.3s;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.replace_button.clicked.connect(self.replace_ips)
        self.replace_layout.addWidget(self.replace_label)
        self.replace_layout.addWidget(self.replace_input)
        self.main_layout.addLayout(self.replace_layout)
        self.main_layout.addWidget(self.replace_button)

        # Replace IP with exclamations section
        self.label_replace_keep = QLabel("Замена IP-адресов (сохранить '!'):", self)
        self.main_layout.addWidget(self.label_replace_keep)

        self.button_replace_keep = QPushButton("Выбрать файл и заменить", self)
        self.button_replace_keep.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border-radius: 10px;
                color: white;
                padding: 12px;
                font-size: 16px;
                transition: background-color 0.3s;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.button_replace_keep.clicked.connect(self.replace_ips_keep_exclamations)
        self.main_layout.addWidget(self.button_replace_keep)

        # New section for replacing third octet with numbers from 1 to 25
        self.label_replace_third_octet = QLabel("Заменить третий октет на числа от 1 до 25:", self)
        self.main_layout.addWidget(self.label_replace_third_octet)

        self.button_replace_third_octet = QPushButton("Заменить третий октет", self)
        self.button_replace_third_octet.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border-radius: 10px;
                color: white;
                padding: 12px;
                font-size: 16px;
                transition: background-color 0.3s;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.button_replace_third_octet.clicked.connect(self.replace_third_octet)
        self.main_layout.addWidget(self.button_replace_third_octet)

    def set_background_image(self):
        # Load the background image if available
        if os.path.exists('background.jpg'):
            self.background_image = QPixmap('background.jpg')  # Replace with your image file
        else:
            print("Background image not found!")
            self.background_image = None

    def paintEvent(self, event):
        # Override paintEvent to draw the background image
        if self.background_image:
            painter = QPainter(self)
            painter.setBrush(QBrush(self.background_image))
            painter.drawRect(self.rect())  # Draw the background image
        super().paintEvent(event)  # Call base class paintEvent to handle other painting

    def show_about(self):
        QMessageBox.information(self, "О программе", "Программа для автоматической работы с конфигурационными файлами маршрутизаторов. by yukimura maybe")

    def clean_file(self):
        input_file = QFileDialog.getOpenFileName(self, "Выберите входной файл")[0]
        if input_file:
            output_file = "clean_config.txt"
            try:
                with open(input_file, 'r') as file:
                    lines = file.readlines()
                with open(output_file, 'w') as file:
                    for line in lines:
                        if '!' not in line:
                            file.write(line)
                QMessageBox.information(self, "Успех", f"Чистая конфигурация сохранена в {output_file}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))

    def replace_ips(self):
        input_file = QFileDialog.getOpenFileName(self, "Выберите входной файл")[0]
        new_octet = self.replace_input.text()
        if input_file and new_octet.isdigit():
            output_file = "catalog_config.txt"
            try:
                with open(input_file, 'r') as file:
                    content = file.read()
                ip_pattern = re.compile(r'192\.168\.\d+\.\d+')
                replacement_ip = f"192.168.{new_octet}.1"
                updated_content = ip_pattern.sub(replacement_ip, content)
                cleaned_content = '\n'.join(line for line in updated_content.splitlines() if '!' not in line)
                with open(output_file, 'w') as file:
                    file.write(cleaned_content)
                QMessageBox.information(self, "Успех", f"IP-адреса заменены и файл очищен. Результат сохранен в {output_file}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))

    def replace_ips_keep_exclamations(self):
        input_file = QFileDialog.getOpenFileName(self, "Выберите входной файл")[0]
        new_octet = self.replace_input.text()
        if input_file and new_octet.isdigit():
            output_file = "config_with_exclamations.txt"
            try:
                with open(input_file, 'r') as file:
                    content = file.read()

                # Regular expression to match IP addresses with any third octet
                ip_pattern = re.compile(r'192\.168\.(\d+)\.(\d+)')

                # Replace only the third octet while keeping the rest of the IP intact
                replacement_ip = f"192.168.{new_octet}.\\2"
                updated_content = ip_pattern.sub(replacement_ip, content)

                with open(output_file, 'w') as file:
                    file.write(updated_content)

                QMessageBox.information(self, "Успех", f"IP-адреса заменены. Результат сохранен в {output_file}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))

    def change_file_dates(self):
        # Open the file date changer window
        self.file_date_changer = FileDateChanger()
        self.file_date_changer.show()

    def open_program_folder(self):
        try:
            folder_path = os.path.dirname(os.path.abspath(__file__))
            if platform.system() == "Windows":
                os.startfile(folder_path)
            elif platform.system() == "Darwin":  # macOS
                os.system(f'open "{folder_path}"')
            else:  # Linux and other Unix-like systems
                os.system(f'xdg-open "{folder_path}"')
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть папку программы: {e}")

    def replace_third_octet(self):
        input_file = QFileDialog.getOpenFileName(self, "Выберите входной файл")[0]
        if input_file:
            output_file = "replaced_third_octet.txt"
            try:
                with open(input_file, 'r') as file:
                    content = file.readlines()

                with open(output_file, 'w') as file:
                    for i in range(1, 26):  # Заменяем на числа от 1 до 25
                        for line in content:
                            # Заменяем третий октет на текущее число
                            updated_line = re.sub(r'192\.168\.(\d+)\.(\d+)', f'192.168.{i}.\\2', line)
                            file.write(updated_line)

                QMessageBox.information(self, "Успех", f"Третий октет заменен на числа от 1 до 25. Результат сохранен в {output_file}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))

    def replace_password(self):
        input_file = QFileDialog.getOpenFileName(self, "Выберите файл")[0]
        if input_file:
            # Запрос пароля для замены
            old_password, ok1 = QInputDialog.getText(self, "Старый пароль", "Введите старый пароль:")
            if not ok1:
                return  # Пользователь отменил ввод

            # Запрос нового пароля
            new_password, ok2 = QInputDialog.getText(self, "Новый пароль", "Введите новый пароль:")
            if not ok2:
                return  # Пользователь отменил ввод

            output_file = "config_with_newpassword.txt"
            try:
                with open(input_file, 'r') as file:
                    content = file.read()

                # Заменяем старый пароль на новый
                updated_content = content.replace(old_password, new_password)

                with open(output_file, 'w') as file:
                    file.write(updated_content)

                QMessageBox.information(self, "Успех", f"Пароль заменен. Результат сохранен в {output_file}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))


if __name__ == "__main__":
    app = QApplication([])  # Ensure QApplication() is called with an empty list
    window = CiscoCleanerApp()
    window.show()
    app.exec()