# MainWindow - entry point after login
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QPushButton, QTableWidget,
    QTableWidgetItem, QLineEdit, QLabel, QCheckBox, QHBoxLayout, QMessageBox
)
from ui.email_dialog import EmailManagementDialog
import sqlite3
import configparser
import logging
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from email.mime.text import MIMEText
import smtplib
from ui.category_matrix import CategoryMatrixTab

# Config and logging
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

logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(message)s')

# Jinja2 setup
env = Environment(loader=FileSystemLoader(template_path.rsplit("/", 1)[0]))
template = env.get_template(template_path.rsplit("/", 1)[1])

def get_db_connection():
    return sqlite3.connect(db_path)

class MainWindow(QWidget):
    def __init__(self, user_id, username):
        super().__init__()
        self.user_id = user_id
        self.username = username
        self.setWindowTitle(f"ISO 50001 Newsletter – Logged in as {username}")

        self.tabs = QTabWidget()
        self.tab_dashboard = QWidget()
        self.tab_customers = QWidget()
        self.tab_categories = CategoryMatrixTab(db_path)
        self.tabs.addTab(self.tab_categories, "Categories & Matrix")


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
        self.table = QTableWidget()
        layout.addWidget(self.send_btn)
        layout.addWidget(self.table)
        self.tab_dashboard.setLayout(layout)
        self.load_recent_changes()

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

    def init_customers(self):
        layout = QVBoxLayout()

        self.customer_name_input = QLineEdit()
        self.customer_email_input = QLineEdit()
        self.customer_active_input = QCheckBox("Active")
        self.add_customer_btn = QPushButton("Add Customer")
        self.customer_table = QTableWidget()

        form_layout = QVBoxLayout()
        form_layout.addWidget(QLabel("Customer Name:"))
        form_layout.addWidget(self.customer_name_input)
        form_layout.addWidget(QLabel("Primary Email (optional):"))
        form_layout.addWidget(self.customer_email_input)
        form_layout.addWidget(self.customer_active_input)
        form_layout.addWidget(self.add_customer_btn)

        layout.addLayout(form_layout)
        layout.addWidget(self.customer_table)
        self.tab_customers.setLayout(layout)

        self.add_customer_btn.clicked.connect(self.add_customer)
        self.load_customers()

    def load_customers(self):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name, active FROM Customers ORDER BY name")
        rows = cur.fetchall()
        self.customer_table.setRowCount(len(rows))
        self.customer_table.setColumnCount(5)
        self.customer_table.setHorizontalHeaderLabels(["ID", "Name", "# Emails", "Active", ""])
        for i, row in enumerate(rows):
            cur.execute("SELECT COUNT(*) FROM CustomerEmails WHERE customer_id = ?", (row[0],))
            email_count = cur.fetchone()[0]
            for j, value in enumerate([row[0], row[1], email_count, row[2]]):
                self.customer_table.setItem(i, j, QTableWidgetItem(str(value)))
            manage_btn = QPushButton("Manage Emails")
            manage_btn.clicked.connect(lambda _, cid=row[0], cname=row[1]: self.open_email_dialog(cid, cname))
            self.customer_table.setCellWidget(i, 4, manage_btn)
        conn.close()

    def open_email_dialog(self, customer_id, customer_name):
        dialog = EmailManagementDialog(customer_id, customer_name, db_path)
        dialog.exec()
        self.load_customers()

    def add_customer(self):
        name = self.customer_name_input.text().strip()
        email = self.customer_email_input.text().strip()
        active = 1 if self.customer_active_input.isChecked() else 0

        if not name:
            QMessageBox.warning(self, "Validation", "Customer name is required.")
            return

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO Customers (name, active) VALUES (?, ?)", (name, active))
        customer_id = cur.lastrowid
        if email:
            cur.execute("INSERT INTO CustomerEmails (customer_id, email) VALUES (?, ?)", (customer_id, email))
        conn.commit()
        conn.close()

        logging.info(f"Added customer: {name}")
        QMessageBox.information(self, "Success", f"Customer '{name}' added.")
        self.customer_name_input.clear()
        self.customer_email_input.clear()
        self.customer_active_input.setChecked(False)
        self.load_customers()
        # This updates the matrix view
        self.tab_categories.refresh_data()

    def send_test_newsletter(self):
        customer = {"customer_name": "Test GmbH", "customer_email": "test@example.com"}
        changes = [{
            "type": "change",
            "effective_date": "2025-07-01",
            "category": "Germany",
            "content": "New rule for energy audits."
        }]
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
