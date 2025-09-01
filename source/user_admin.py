import bcrypt
from db_init import get_db, audit

def create_user(admin_id, username, password, role="viewer"):
    conn = get_db()
    c = conn.cursor()
    h = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    c.execute("INSERT INTO users(username,password_hash,role) VALUES (?,?,?)", (username, h, role))
    conn.commit()
    conn.close()
    audit(admin_id, "create_user", username, f"role={role}")

def delete_user(admin_id, username):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE username=?", (username,))
    conn.commit()
    conn.close()
    audit(admin_id, "delete_user", username)

def list_users():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id,username,role FROM users")
    rows = c.fetchall()
    conn.close()
    return rows
