import tkinter as tk
import threading, time, shutil, os
from tkinter import messagebox, simpledialog
from db_init import init_db, get_db, audit
import books, borrow, source.user_admin as user_admin

BACKUP_DIR = "backup"
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

class App:
    def __init__(self, master, user_id, role):
        self.master, self.user_id, self.role = master, user_id, role
        master.title(f"Library Manager - Role: {role}")
        tk.Button(master, text="📚 Manage Books", command=self.manage_books).pack(fill="x")
        tk.Button(master, text="🔍 Search ISBN", command=self.search_isbn).pack(fill="x")
        tk.Button(master, text="📖 Borrow/Return", command=self.borrow_books).pack(fill="x")
        tk.Button(master, text="👤 User Admin", command=self.user_admin).pack(fill="x")
        tk.Button(master, text="📌 Audit Logs", command=self.show_audit).pack(fill="x")
        tk.Button(master, text="📤 Backup Now", command=self.backup).pack(fill="x")

        threading.Thread(target=self.auto_backup, daemon=True).start()

    def manage_books(self):
        if self.role not in ("admin", "staff"):
            return messagebox.showerror("Denied", "No permission")
        win = tk.Toplevel(self.master)
        win.title("Books")
        tk.Button(win, text="Add Book", command=lambda: books.add_book(self.user_id, win)).pack()
        tk.Button(win, text="Delete Book", command=lambda: self.delete_book(win)).pack()

    def delete_book(self, parent):
        isbn = simpledialog.askstring("Delete", "ISBN:", parent=parent)
        if isbn:
            books.delete_book(self.user_id, isbn)

    def search_isbn(self):
        code = simpledialog.askstring("Search", "Enter ISBN:")
        row = books.search_book(code)
        if row:
            messagebox.showinfo("Result", f"{row[0]} by {row[1]} @ {row[2]} (Available:{row[3]})")
        else:
            messagebox.showwarning("Not Found", "No book found")

    def borrow_books(self):
        win = tk.Toplevel(self.master)
        tk.Button(win, text="Borrow Book", command=lambda: borrow.borrow_book(self.user_id)).pack()
        tk.Button(win, text="Return Book", command=lambda: borrow.return_book(self.user_id)).pack()

    def user_admin(self):
        if self.role != "admin":
            return messagebox.showerror("Denied", "Admin only")
        win = tk.Toplevel(self.master)
        tk.Button(win, text="Add User", command=lambda: self.add_user(win)).pack()
        tk.Button(win, text="List Users", command=self.show_users).pack()

    def add_user(self, parent):
        u = simpledialog.askstring("New User", "Username:", parent=parent)
        p = simpledialog.askstring("Password", "Password:", show="*", parent=parent)
        r = simpledialog.askstring("Role", "Role (admin/staff/viewer):", parent=parent)
        if u and p and r:
            user_admin.create_user(self.user_id, u, p, r)
            messagebox.showinfo("OK", "User added")

    def show_users(self):
        rows = user_admin.list_users()
        msg = "\n".join([f"{r[0]} - {r[1]} ({r[2]})" for r in rows])
        messagebox.showinfo("Users", msg)

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

    def backup(self):
        fname = os.path.join(BACKUP_DIR, f"backup_{int(time.time())}.db")
        shutil.copy("library.db", fname)
        messagebox.showinfo("Backup", f"Saved {fname}")

    def auto_backup(self):
        while True:
            self.backup()
            time.sleep(600)

# ======== AUTO INIT ADMIN USER ==========
def ensure_admin_user():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username='admin'")
    if not c.fetchone():
        # tạo admin/admin
        user_admin.create_user("system", "admin", "admin", "admin")
        print("[INFO] Default admin user created (username=admin, password=admin)")
    conn.close()
# ========================================

if __name__ == "__main__":
    init_db()
    ensure_admin_user()   # auto add admin nếu chưa có
    import login
    root = tk.Tk()
    root.state("zoomed") 
    login.LoginWindow(root)
    root.mainloop()
