import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
import bcrypt
from db_init import get_db
from main import App
from PIL import Image, ImageTk


class LoginWindow:
    def __init__(self, master):
        self.master = master
        master.title("📚 Library Login")
        master.geometry("900x600")
        master.resizable(True, True)

        # style business sáng
        style = tb.Style("flatly")

        # căn giữa cửa sổ
        window_width, window_height = 900, 600
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        x_cordinate = int((screen_width / 2) - (window_width / 2))
        y_cordinate = int((screen_height / 2) - (window_height / 2))
        master.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")

        # ===== Background (logo / ảnh full màn hình) =====
        try:
            bg_img = Image.open("image/logo.png").resize((screen_width, screen_height))
            # Làm mờ nhẹ background
            bg_img = bg_img.convert("RGBA")
            alpha = 100  # chỉnh độ mờ (0 = trong suốt, 255 = rõ nét)
            for y in range(bg_img.size[1]):
                for x in range(bg_img.size[0]):
                    r, g, b, a = bg_img.getpixel((x, y))
                    bg_img.putpixel((x, y), (r, g, b, alpha))

            self.bg_photo = ImageTk.PhotoImage(bg_img)
            bg_label = tb.Label(master, image=self.bg_photo)
            bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        except Exception as e:
            print("Không load được background:", e)

        # ===== Frame Login nổi trên nền =====
        frame = tb.Frame(master, padding=30, bootstyle="light")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tb.Label(frame, text="Library Management - Quản lý thư viện", font=("Helvetica", 20, "bold")).pack(pady=10)

        # username
        self.username = tb.Entry(frame, bootstyle=INFO, font=("Helvetica", 12))
        self.username.insert(0, "Username")
        self.username.pack(pady=10, fill=X)

        # password
        self.password = tb.Entry(frame, show="*", bootstyle=INFO, font=("Helvetica", 12))
        self.password.pack(pady=10, fill=X)

        # login button (màu vàng vàng)
        login_btn = tb.Button(frame, text="Login", bootstyle=WARNING, command=self.login)
        login_btn.pack(pady=20, fill=X)

        # enter key
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
            self.master.destroy()
            root = tb.Window(themename="flatly")
            root.state("zoomed")  # bung toàn màn hình
            App(root, row[0], row[2])
            root.mainloop()
        else:
            messagebox.showerror("Error", "Invalid login")
