from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QComboBox, QCheckBox, QHBoxLayout, QMessageBox
)
import sqlite3

class CategoryMatrixTab(QWidget):
    def __init__(self, db_path):
        super().__init__()
        self.db_path = db_path
        self.all_items = []
        self.mapped_ids = set()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["Customer View", "Category View"])
        self.mode_selector.currentIndexChanged.connect(self.refresh_ui)
        self.layout.addWidget(QLabel("Select Mode:"))
        self.layout.addWidget(self.mode_selector)

        self.selection_box = QComboBox()
        self.selection_box.currentIndexChanged.connect(self.render_checklist)
        self.layout.addWidget(self.selection_box)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        self.search_input.textChanged.connect(self.filter_checklist)
        self.layout.addWidget(self.search_input)

        self.check_table = QTableWidget()
        self.layout.addWidget(self.check_table)

        self.refresh_ui()

    def get_db_connection(self):
        return sqlite3.connect(self.db_path)

    def refresh_ui(self):
        mode = self.mode_selector.currentText()
        conn = self.get_db_connection()
        cur = conn.cursor()

        if mode == "Customer View":
            cur.execute("SELECT id, name FROM Customers WHERE active = 1 ORDER BY name")
        else:
            cur.execute("SELECT id, scope || ' – ' || description FROM Categories ORDER BY scope, description")

        items = cur.fetchall()
        self.selection_box.clear()
        for item in items:
            self.selection_box.addItem(item[1], item[0])

        conn.close()
        self.render_checklist()

    def render_checklist(self):
        mode = self.mode_selector.currentText()
        selected_id = self.selection_box.currentData()
        if selected_id is None:
            return

        conn = self.get_db_connection()
        cur = conn.cursor()

        if mode == "Customer View":
            cur.execute("SELECT id, scope || ' – ' || description FROM Categories ORDER BY scope, description")
            self.all_items = cur.fetchall()
            cur.execute("SELECT category_id FROM CustomerCategoryMapping WHERE customer_id = ?", (selected_id,))
            self.mapped_ids = {row[0] for row in cur.fetchall()}
        else:
            cur.execute("SELECT id, name FROM Customers WHERE active = 1 ORDER BY name")
            self.all_items = cur.fetchall()
            cur.execute("SELECT customer_id FROM CustomerCategoryMapping WHERE category_id = ?", (selected_id,))
            self.mapped_ids = {row[0] for row in cur.fetchall()}

        conn.close()
        self.filter_checklist()

    def filter_checklist(self):
        search_text = self.search_input.text().lower()
        mode = self.mode_selector.currentText()
        selected_id = self.selection_box.currentData()

        filtered_items = [item for item in self.all_items if search_text in item[1].lower()]

        self.check_table.setRowCount(len(filtered_items))
        self.check_table.setColumnCount(2)
        self.check_table.setHorizontalHeaderLabels(["Name", "Mapped"])

        for i, (item_id, label) in enumerate(filtered_items):
            self.check_table.setItem(i, 0, QTableWidgetItem(label))
            checkbox = QCheckBox()
            checkbox.setChecked(item_id in self.mapped_ids)
            checkbox.stateChanged.connect(self.get_checkbox_handler(mode, selected_id, item_id))
            self.check_table.setCellWidget(i, 1, checkbox)

    def get_checkbox_handler(self, mode, selected_id, target_id):
        def handler(state):
            conn = self.get_db_connection()
            cur = conn.cursor()
            if mode == "Customer View":
                customer_id, category_id = selected_id, target_id
            else:
                customer_id, category_id = target_id, selected_id

            if state == 2:
                cur.execute(
                    "INSERT OR IGNORE INTO CustomerCategoryMapping (customer_id, category_id) VALUES (?, ?)",
                    (customer_id, category_id)
                )
            else:
                cur.execute(
                    "DELETE FROM CustomerCategoryMapping WHERE customer_id = ? AND category_id = ?",
                    (customer_id, category_id)
                )
            conn.commit()
            conn.close()
        return handler

