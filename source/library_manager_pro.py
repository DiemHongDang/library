import sys
import subprocess
import importlib

# ================= Auto Install Missing Packages =================
# required = [
#     "bcrypt", "pillow", "opencv-python", "pyzbar", "qrcode"
# ]

# for pkg in required:
#     try:
#         importlib.import_module(pkg if pkg != "pillow" else "PIL")
#     except ImportError:
#         print(f"[INFO] Installing missing package: {pkg}")
#         subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

# ================== Imports ==================
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import sqlite3, bcrypt, os, shutil, time, threading, qrcode
from PIL import Image, ImageTk
#import cv2
#from pyzbar.pyzbar import decode

DB = "library.db"
BACKUP_DIR = "backup"
ASSET_DIR = "assets"

if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)
if not os.path.exists(ASSET_DIR):
    os.makedirs(ASSET_DIR)

# ================= DB Helper =================
def get_db():
    return sqlite3.connect(DB)

def audit(user_id, action, target, details=""):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO audit_logs(user_id,action,target,details) VALUES (?,?,?,?)",
              (user_id, action, target, details))
    conn.commit()
    conn.close()

# ================= Login Window =================
class LoginWindow:
    def __init__(self, master):
        self.master = master
        master.title("Library Login")
        tk.Label(master, text="Username").pack()
        self.username = tk.Entry(master)
        self.username.pack()
        tk.Label(master, text="Password").pack()
        self.password = tk.Entry(master, show="*")
        self.password.pack()
        tk.Button(master, text="Login", command=self.login).pack()

    def login(self):
        user, pw = self.username.get(), self.password.get()
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT id,password_hash,role FROM users WHERE username=?", (user,))
        row = c.fetchone()
        conn.close()
        if row and bcrypt.checkpw(pw.encode(), row[1].encode()):
            self.master.destroy()
            root = tk.Tk()
            App(root, row[0], row[2])
            root.mainloop()
        else:
            messagebox.showerror("Error", "Invalid login")

# ================= Main App =================
class App:
    def __init__(self, master, user_id, role):
        self.master, self.user_id, self.role = master, user_id, role
        master.title(f"Library Manager - Role: {role}")
        tk.Button(master, text="📚 Manage Books", command=self.manage_books).pack(fill="x")
        tk.Button(master, text="🔍 Search ISBN", command=self.search_isbn).pack(fill="x")
        tk.Button(master, text="📖 Borrow/Return", command=self.borrow_books).pack(fill="x")
        tk.Button(master, text="📌 Audit Logs", command=self.show_audit).pack(fill="x")
        tk.Button(master, text="📤 Backup Now", command=self.backup).pack(fill="x")
        tk.Button(master, text="🔑 Change Password", command=self.change_pw).pack(fill="x")

        # Auto backup every 10 min
        threading.Thread(target=self.auto_backup, daemon=True).start()

    def manage_books(self):
        if self.role not in ("admin", "staff"):
            return messagebox.showerror("Denied", "No permission")
        win = tk.Toplevel(self.master)
        win.title("Books")
        tk.Button(win, text="Add Book", command=lambda: self.add_book(win)).pack()

    def add_book(self, parent):
        title = simpledialog.askstring("Title", "Book title:", parent=parent)
        author = simpledialog.askstring("Author", "Book author:", parent=parent)
        isbn = simpledialog.askstring("ISBN", "Book ISBN:", parent=parent)
        loc = simpledialog.askstring("Location", "Shelf/Desk:", parent=parent)
        if title and isbn:
            conn = get_db()
            c = conn.cursor()
            c.execute("INSERT INTO books(title,author,isbn,location) VALUES (?,?,?,?)",
                      (title, author, isbn, loc))
            conn.commit()
            conn.close()
            audit(self.user_id, "add_book", isbn, title)
            # create QR
            img = qrcode.make(isbn)
            img.save(os.path.join(ASSET_DIR, f"{isbn}.png"))
            messagebox.showinfo("Saved", "Book added & QR generated!")

    def search_isbn(self):
        code = simpledialog.askstring("Search", "Enter ISBN:")
        if code:
            conn = get_db()
            c = conn.cursor()
            c.execute("SELECT title,author,location,available FROM books WHERE isbn=?", (code,))
            row = c.fetchone()
            conn.close()
            if row:
                messagebox.showinfo("Result",
                                    f"{row[0]} by {row[1]} @ {row[2]} (Available:{row[3]})")
            else:
                messagebox.showwarning("Not Found", "No book found")

    def borrow_books(self):
        if self.role == "viewer":
            return messagebox.showerror("Denied", "View only")
        isbn = simpledialog.askstring("Borrow", "Enter ISBN:")
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT id,available FROM books WHERE isbn=?", (isbn,))
        book = c.fetchone()
        if not book:
            return messagebox.showerror("Error", "Book not found")
        if book[1] == 0:
            return messagebox.showerror("Error", "Not available")
        c.execute("INSERT INTO borrows(user_id,book_id) VALUES (?,?)", (self.user_id, book[0]))
        c.execute("UPDATE books SET available=0 WHERE id=?", (book[0],))
        conn.commit()
        conn.close()
        audit(self.user_id, "borrow", isbn)
        messagebox.showinfo("OK", "Borrowed!")

    def show_audit(self):
        if self.role != "admin":
            return messagebox.showerror("Denied", "Admin only")
        win = tk.Toplevel(self.master)
        win.title("Audit Logs")
        txt = tk.Text(win)
        txt.pack(fill="both", expand=True)
        conn = get_db()
        c = conn.cursor()
        for r in c.execute("SELECT user_id,action,target,timestamp FROM audit_logs ORDER BY id DESC LIMIT 50"):
            txt.insert("end", f"{r}\n")
        conn.close()

    def change_pw(self):
        pw = simpledialog.askstring("Password", "New Password:", show="*")
        if pw:
            h = bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
            conn = get_db()
            c = conn.cursor()
            c.execute("UPDATE users SET password_hash=? WHERE id=?", (h, self.user_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Done", "Password changed")

    def backup(self):
        fname = os.path.join(BACKUP_DIR, f"backup_{int(time.time())}.db")
        shutil.copy(DB, fname)
        messagebox.showinfo("Backup", f"Saved {fname}")

    def auto_backup(self):
        while True:
            self.backup()
            time.sleep(600)  # 10min


if __name__ == "__main__":
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()
