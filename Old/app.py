# ISO 50001 Newsletter Application (PySide6 Desktop App)
# Now includes Customer Management UI

import sys
import os
import smtplib
import sqlite3
import logging
import configparser
from datetime import datetime
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QTabWidget, QCheckBox
)

# --------------- Configuration -------------------
config = configparser.ConfigParser()
config.read('config.ini')

db_path = config['APP']['db_path']
template_path = config['APP']['template_path']
log_file = config['APP']['log_file']

smtp_host = config['SMTP']['host']
smtp_port = int(config['SMTP']['port'])
smtp_user = config['SMTP']['username']
smtp_pass = config['SMTP']['password']
smtp_tls = config['SMTP'].getboolean('use_tls')

# Setup logging
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(message)s')

# Setup Jinja2 environment
env = Environment(loader=FileSystemLoader(os.path.dirname(template_path)))
template = env.get_template(os.path.basename(template_path))

# --------------- Database Helper -------------------
def get_db_connection():
    return sqlite3.connect(db_path)

# --------------- Login UI -------------------
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

        if row and password == row[1]:  # In production, use proper hashing (bcrypt)
            logging.info(f"User {username} logged in.")
            self.accept_login(row[0], username)
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid credentials")

    def accept_login(self, user_id, username):
        self.main_window = MainWindow(user_id, username)
        self.main_window.show()
        self.close()


# --------------- Main UI -------------------
class MainWindow(QWidget):
    def __init__(self, user_id, username):
        super().__init__()
        self.user_id = user_id
        self.username = username
        self.setWindowTitle(f"ISO 50001 Newsletter – Logged in as {username}")

        self.tabs = QTabWidget()
        self.tab_dashboard = QWidget()
        self.tab_customers = QWidget()

        self.tabs.addTab(self.tab_dashboard, "Dashboard")
        self.tabs.addTab(self.tab_customers, "Customers")

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

        self.init_dashboard()
        self.init_customers()

    def init_dashboard(self):
        layout = QVBoxLayout()

        self.send_btn = QPushButton("Send Test Newsletter")
        self.send_btn.clicked.connect(self.send_test_newsletter)
        layout.addWidget(self.send_btn)

        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.tab_dashboard.setLayout(layout)
        self.load_recent_changes()

    def init_customers(self):
        layout = QVBoxLayout()

        self.customer_name_input = QLineEdit()
        self.customer_email_input = QLineEdit()
        self.customer_active_input = QCheckBox("Active")
        self.add_customer_btn = QPushButton("Add Customer")

        form_layout = QVBoxLayout()
        form_layout.addWidget(QLabel("Customer Name:"))
        form_layout.addWidget(self.customer_name_input)
        form_layout.addWidget(QLabel("Customer Email:"))
        form_layout.addWidget(self.customer_email_input)
        form_layout.addWidget(self.customer_active_input)
        form_layout.addWidget(self.add_customer_btn)

        self.add_customer_btn.clicked.connect(self.add_customer)

        self.customer_table = QTableWidget()
        layout.addLayout(form_layout)
        layout.addWidget(self.customer_table)

        self.tab_customers.setLayout(layout)
        self.load_customers()

    def load_recent_changes(self):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, content, effective_date FROM RegulatoryChanges ORDER BY added_at DESC LIMIT 10")
        rows = cur.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Content", "Effective Date"])
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(value)))

    def load_customers(self):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name, email, active FROM Customers ORDER BY name")
        rows = cur.fetchall()
        conn.close()

        self.customer_table.setRowCount(len(rows))
        self.customer_table.setColumnCount(4)
        self.customer_table.setHorizontalHeaderLabels(["ID", "Name", "Email", "Active"])
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                self.customer_table.setItem(i, j, QTableWidgetItem(str(value)))

    def add_customer(self):
        name = self.customer_name_input.text().strip()
        email = self.customer_email_input.text().strip()
        active = 1 if self.customer_active_input.isChecked() else 0

        if not name or not email:
            QMessageBox.warning(self, "Validation", "Name and Email are required.")
            return

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO Customers (name, email, active) VALUES (?, ?, ?)", (name, email, active))
        conn.commit()
        conn.close()

        logging.info(f"Added customer: {name} <{email}>")
        QMessageBox.information(self, "Success", f"Customer '{name}' added.")
        self.customer_name_input.clear()
        self.customer_email_input.clear()
        self.customer_active_input.setChecked(False)
        self.load_customers()

    def send_test_newsletter(self):
        customer = {"customer_name": "Test GmbH", "customer_email": "test@example.com"}
        changes = [
            {"type": "change", "effective_date": "2025-07-01", "category": "Germany", "content": "New rule for energy audits."}
        ]
        html = template.render(
            quarter="Q2 2025",
            customer_name=customer["customer_name"],
            customer_email=customer["customer_email"],
            current_year=datetime.now().year,
            changes=changes
        )

        msg = MIMEText(html, "html")
        msg["Subject"] = "Test ISO 50001 Update"
        msg["From"] = smtp_user
        msg["To"] = customer["customer_email"]

        try:
            server = smtplib.SMTP(smtp_host, smtp_port)
            if smtp_tls:
                server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, [customer["customer_email"]], msg.as_string())
            server.quit()
            logging.info(f"Sent test newsletter to {customer['customer_email']}")
            QMessageBox.information(self, "Success", f"Test newsletter sent to {customer['customer_email']}")
        except Exception as e:
            logging.error(f"Failed to send email: {e}")
            QMessageBox.critical(self, "Error", f"Failed to send email: {str(e)}")


# --------------- Application Entry -------------------
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
