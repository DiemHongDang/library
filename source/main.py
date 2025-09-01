import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading, time, shutil, os
from db_init import DB, init_db, get_db
import books, borrow, user_admin
import login   # để gọi lại màn hình login
from ui_theme import apply_theme, btn_style, title_style   # lấy style + theme

BACKUP_DIR = "backup"
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)


class App:
    def __init__(self, master, user_id, role):
        self.master, self.user_id, self.role = master, user_id, role

        # Áp dụng theme business + background
        apply_theme(master, title=f"Library Manager - Role: {role}", width=1000, height=700)

        # === Container chính ===
        container = tk.Frame(master, bg="#F5F5F5", bd=2, relief="groove")
        container.place(relx=0.5, rely=0.5, anchor="center", width=1000, height=650)

        # === Tiêu đề ===
        title = tk.Label(container, text="📚 Library Manager - Quản lý Thư viện", **title_style)
        title.pack(pady=10)

        # === Notebook để chứa các tab ===
        self.notebook = ttk.Notebook(container)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # === Frame menu bên trái ===
        menu_frame = tk.Frame(container, bg="white")
        menu_frame.pack(side="left", fill="y", padx=5, pady=5)

        # === Các nút chức năng ===
        tk.Button(menu_frame, text="📖 Manage Books", command=self.manage_books, **btn_style).pack(pady=5, fill="x")
        tk.Button(menu_frame, text="🔍 Search ISBN", command=self.search_isbn, **btn_style).pack(pady=5, fill="x")
        tk.Button(menu_frame, text="📗 Borrow / Return", command=self.borrow_books, **btn_style).pack(pady=5, fill="x")
        tk.Button(menu_frame, text="👤 User Admin", command=self.user_admin, **btn_style).pack(pady=5, fill="x")
        tk.Button(menu_frame, text="📝 Audit Logs", command=self.show_audit, **btn_style).pack(pady=5, fill="x")
        tk.Button(menu_frame, text="💾 Backup Now", command=self.backup, **btn_style).pack(pady=5, fill="x")
        tk.Button(menu_frame, text="🚪 Logout", command=self.logout, **btn_style).pack(pady=5, fill="x")
        tk.Button(menu_frame, text="❌ Exit", command=master.quit, **btn_style).pack(pady=5, fill="x")

        # Auto backup chạy nền
        threading.Thread(target=self.auto_backup, daemon=True).start()

    # ========= Hàm mở tab =========
    def open_tab(self, title):
        """Nếu tab chưa mở thì tạo, nếu rồi thì chuyển sang"""
        for i in range(len(self.notebook.tabs())):
            if self.notebook.tab(i, "text") == title:
                self.notebook.select(i)
                return None
        frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(frame, text=title)
        self.notebook.select(len(self.notebook.tabs()) - 1)
        return frame

    # ========= Các chức năng =========
    def manage_books(self):
        if self.role not in ("admin", "staff"):
            return messagebox.showerror("Denied", "No permission")
        tab = self.open_tab("Manage Books")
        if tab:
            tk.Button(tab, text="Add Book", command=lambda: books.add_book(self.user_id, tab)).pack(pady=5)
            tk.Button(tab, text="Delete Book", command=lambda: self.delete_book(tab)).pack(pady=5)

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
        tab = self.open_tab("Borrow / Return")
        if tab:
            tk.Button(tab, text="Borrow Book", command=lambda: borrow.borrow_book(self.user_id)).pack(pady=5)
            tk.Button(tab, text="Return Book", command=lambda: borrow.return_book(self.user_id)).pack(pady=5)

    def user_admin(self):
        if self.role != "admin":
            return messagebox.showerror("Denied", "Admin only")
        tab = self.open_tab("User Admin")
        if tab:
            tk.Button(tab, text="Add User", command=lambda: self.add_user(tab)).pack(pady=5)
            tk.Button(tab, text="List Users", command=self.show_users).pack(pady=5)

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
        tab = self.open_tab("Audit Logs")
        if tab:
            txt = tk.Text(tab)
            txt.pack(fill="both", expand=True)
            conn = get_db()
            c = conn.cursor()
            for r in c.execute("SELECT user_id,action,target,timestamp FROM audit_logs ORDER BY id DESC LIMIT 50"):
                txt.insert("end", f"{r}\n")
            conn.close()

    def backup(self):        
        fname = os.path.join(BACKUP_DIR, f"backup_{int(time.time())}.db")
        shutil.copy(DB, fname)

    def auto_backup(self):
        while True:
            self.backup()
            time.sleep(600)

    # ===== Hàm Logout =====
    def logout(self):
        self.master.destroy()
        root = tk.Tk()
        root.state("zoomed")
        apply_theme(root, title="Library Manager - Login")
        login.LoginWindow(root)
        root.mainloop()


# ======== AUTO INIT ADMIN USER ========== 
def ensure_admin_user():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username='admin'")
    if not c.fetchone():
        user_admin.create_user("system", "admin", "admin", "admin")
        print("[INFO] Default admin user created (username=admin, password=admin)")
    conn.close()
# ========================================

if __name__ == "__main__":
    init_db()
    ensure_admin_user()
    root = tk.Tk()
    root.state("zoomed") 
    login.LoginWindow(root)
    root.mainloop()
        