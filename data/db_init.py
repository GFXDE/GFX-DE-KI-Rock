import sqlite3

db_path = "data/iso_newsletter_app.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.executescript("""
CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME
);

CREATE TABLE IF NOT EXISTS Customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS CustomerEmails (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES Customers(id),
    email TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Categories (
    id INTEGER PRIMARY KEY,
    scope TEXT NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS RegulatoryChanges (
    id INTEGER PRIMARY KEY,
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    added_by_user_id INTEGER NOT NULL REFERENCES Users(id),
    effective_date DATE,
    type TEXT CHECK(type IN ('change', 'frist', 'note', 'news')) NOT NULL,
    category_id INTEGER REFERENCES Categories(id),
    content TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS CustomerCategoryMapping (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER REFERENCES Customers(id),
    category_id INTEGER REFERENCES Categories(id)
);

CREATE TABLE IF NOT EXISTS NewsletterDispatch (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER REFERENCES Customers(id),
    sent_at DATETIME,
    change_ids TEXT,
    status TEXT CHECK(status IN ('sent', 'failed', 'pending')),
    error_message TEXT,
    opened_at DATETIME,
    clicked_at DATETIME
);

CREATE TABLE IF NOT EXISTS AuditLog (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES Users(id),
    action TEXT NOT NULL,
    table_name TEXT,
    row_id INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    details TEXT
);

-- Insert default user: admin / admin
INSERT OR IGNORE INTO Users (username, password_hash, full_name)
VALUES ('admin', 'admin', 'Admin User');
""")

conn.commit()
conn.close()

print("✅ Database initialized.")
