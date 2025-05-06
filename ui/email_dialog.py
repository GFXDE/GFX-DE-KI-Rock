# EmailManagementDialog - move from earlier response
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHBoxLayout, QMessageBox
)
import sqlite3

class EmailManagementDialog(QDialog):
    def __init__(self, customer_id, customer_name, db_path):
        super().__init__()
        self.setWindowTitle(f"Manage Emails for {customer_name}")
        self.customer_id = customer_id
        self.db_path = db_path

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.email_input = QLineEdit()
        self.add_email_button = QPushButton("Add Email")
        self.add_email_button.clicked.connect(self.add_email)

        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("New Email:"))
        input_layout.addWidget(self.email_input)
        input_layout.addWidget(self.add_email_button)
        self.layout.addLayout(input_layout)

        self.email_table = QTableWidget()
        self.email_table.setColumnCount(2)
        self.email_table.setHorizontalHeaderLabels(["Email", ""])
        self.layout.addWidget(self.email_table)

        self.load_emails()

    def get_db_connection(self):
        return sqlite3.connect(self.db_path)

    def load_emails(self):
        conn = self.get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, email FROM CustomerEmails WHERE customer_id = ?", (self.customer_id,))
        rows = cur.fetchall()
        conn.close()

        self.email_table.setRowCount(len(rows))
        for i, (email_id, email) in enumerate(rows):
            self.email_table.setItem(i, 0, QTableWidgetItem(email))
            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda _, eid=email_id: self.delete_email(eid))
            self.email_table.setCellWidget(i, 1, delete_btn)

    def add_email(self):
        email = self.email_input.text().strip()
        if not email:
            QMessageBox.warning(self, "Validation Error", "Email address cannot be empty.")
            return

        conn = self.get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO CustomerEmails (customer_id, email) VALUES (?, ?)", (self.customer_id, email))
        conn.commit()
        conn.close()

        self.email_input.clear()
        self.load_emails()

    def delete_email(self, email_id):
        conn = self.get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM CustomerEmails WHERE id = ?", (email_id,))
        conn.commit()
        conn.close()
        self.load_emails()
