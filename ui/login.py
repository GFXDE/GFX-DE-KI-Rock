from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from ui.main_window import MainWindow
import sqlite3
import configparser
import logging

# Read config
config = configparser.ConfigParser()
config.read('config.ini')
db_path = config['APP']['db_path']
log_file = config['APP']['log_file']

# Setup logging (fallback if not set in main)
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(message)s')

def get_db_connection():
    return sqlite3.connect(db_path)

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ISO 50001 Newsletter Login")
        layout = QVBoxLayout()

        self.user_input = QLineEdit()
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.login_btn = QPushButton("Login")

        layout.addWidget(QLabel("Username:"))
        layout.addWidget(self.user_input)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.pass_input)
        layout.addWidget(self.login_btn)

        self.login_btn.clicked.connect(self.handle_login)
        self.setLayout(layout)

    def handle_login(self):
        username = self.user_input.text()
        password = self.pass_input.text()

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, password_hash FROM Users WHERE username = ?", (username,))
        row = cur.fetchone()
        conn.close()

        if row and password == row[1]:  # Replace with hash check in prod
            logging.info(f"User {username} logged in.")
            self.accept_login(row[0], username)
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid credentials")

    def accept_login(self, user_id, username):
        self.main_window = MainWindow(user_id, username)
        self.main_window.show()
        self.close()
