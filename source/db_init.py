import sqlite3, os

# Đường dẫn tuyệt đối tới thư mục db
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "db")

# tạo thư mục db nếu chưa có
os.makedirs(DB_DIR, exist_ok=True)

DB = os.path.join(DB_DIR, "library.db")

def get_db():
    return sqlite3.connect(DB)

def init_db():
    conn = get_db()
    c = conn.cursor()
    # users
    c.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password_hash TEXT,
        role TEXT
    )""")
    # books
    c.execute("""CREATE TABLE IF NOT EXISTS books(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        author TEXT,
        isbn TEXT UNIQUE,
        location TEXT,
        available INTEGER DEFAULT 1
    )""")
    # borrows
    c.execute("""CREATE TABLE IF NOT EXISTS borrows(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        book_id INTEGER,
        borrowed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        returned_at TIMESTAMP
    )""")
    # audit
    c.execute("""CREATE TABLE IF NOT EXISTS audit_logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT,
        target TEXT,
        details TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.commit()
    conn.close()

def audit(user_id, action, target, details=""):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO audit_logs(user_id,action,target,details) VALUES (?,?,?,?)",
              (user_id, action, target, details))
    conn.commit()
    conn.close()
