import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
import bcrypt
from db_init import get_db
from main import App
from ui_theme import apply_theme


class LoginWindow:
    def __init__(self, master):
        self.master = master   # 🔑 giữ lại master
        apply_theme(master, "📚 Library Login", 900, 600)

        frame = tb.Frame(master, padding=30, bootstyle="light")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tb.Label(frame, text="Library Management - Quản lý Thư viện", 
                 font=("Helvetica", 20, "bold")).pack(pady=10)

        # Username entry
        self.username = tb.Entry(frame, bootstyle=INFO, font=("Helvetica", 12))
        self.username.insert(0, "username")
        self.username.bind("<FocusIn>", lambda e: self._clear_placeholder(self.username, "username"))
        self.username.bind("<FocusOut>", lambda e: self._add_placeholder(self.username, "username"))
        self.username.pack(pady=10, fill=X)

        # Password entry
        self.password = tb.Entry(frame, bootstyle=INFO, font=("Helvetica", 12))
        self.password.insert(0, "password")
        self.password.bind("<FocusIn>", lambda e: self._clear_placeholder(self.password, "password", is_password=True))
        self.password.bind("<FocusOut>", lambda e: self._add_placeholder(self.password, "password", is_password=True))
        self.password.pack(pady=10, fill=X)

        login_btn = tb.Button(frame, text="Login", bootstyle=WARNING, command=self.login)
        login_btn.pack(pady=20, fill=X)

        # 🔑 bind phím Enter
        self.username.bind("<Return>", lambda e: self.login())
        self.password.bind("<Return>", lambda e: self.login())

        self.username.focus()

    def login(self):
        user, pw = self.username.get(), self.password.get()
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT id,password_hash,role FROM users WHERE username=?", (user,))
        row = c.fetchone()
        conn.close()

        if row and bcrypt.checkpw(pw.encode(), row[1].encode()):
            self.master.destroy()  # đóng login
            root = tb.Window(themename="flatly")
            root.state("zoomed")   # mở main app toàn màn hình
            App(root, row[0], row[2])
            root.mainloop()
        else:
            messagebox.showerror("Error", "Invalid login")
    def _clear_placeholder(self, entry, placeholder, is_password=False):
        """Xóa placeholder khi focus"""
        if entry.get() == placeholder:
            entry.delete(0, "end")
            if is_password:
                entry.config(show="*")

    def _add_placeholder(self, entry, placeholder, is_password=False):
        """Thêm lại placeholder khi để trống"""
        if entry.get() == "":
            entry.insert(0, placeholder)
            if is_password:
                entry.config(show="") 
