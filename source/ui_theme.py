import ttkbootstrap as tb
from PIL import Image, ImageTk

# ================== STYLE DÙNG CHUNG ==================
bg_color = "#f0f4f7"   # màu nền sáng
title_style = {
    "font": ("Segoe UI", 18, "bold"),
    "bg": "white",
    "fg": "#2c3e50"
}
btn_style = {
    "font": ("Segoe UI", 12),
    "bg": "#2c3e50",
    "fg": "white",
    "relief": "flat",
    "activebackground": "#34495e",
    "activeforeground": "white",
    "width": 20,
    "height": 2
}
# =======================================================

import ttkbootstrap as tb
from PIL import Image, ImageTk, ImageEnhance
import tkinter as tk

def apply_theme(master, title="Library App", width=900, height=600):
    """Áp dụng style business + background logo full window"""
    master.title(title)
    master.geometry(f"{width}x{height}")
    master.resizable(True, True)

    # style business
    style = tb.Style("flatly")

    # căn giữa cửa sổ
    screen_width = master.winfo_screenwidth()
    screen_height = master.winfo_screenheight()
    x_cordinate = int((screen_width / 2) - (width / 2))
    y_cordinate = int((screen_height / 2) - (height / 2))
    master.geometry(f"{width}x{height}+{x_cordinate}+{y_cordinate}")

    # ===== Background =====
    try:
        original_img = Image.open("image/logo.png").convert("RGBA")

        # Làm mờ ảnh một chút (opacity ~80%)
        enhancer = ImageEnhance.Brightness(original_img)
        original_img = enhancer.enhance(0.8)

        def resize_bg(event=None):
            w, h = master.winfo_width(), master.winfo_height()
            if w <= 1 or h <= 1:
                return
            resized = original_img.resize((w, h), Image.Resampling.LANCZOS)
            bg_photo = ImageTk.PhotoImage(resized)
            bg_label.config(image=bg_photo)
            bg_label.image = bg_photo

        bg_label = tk.Label(master)
        bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)

        # auto resize khi thay đổi kích thước window
        master.bind("<Configure>", resize_bg)
        resize_bg()

    except Exception as e:
        print("⚠️ Không load được background:", e)

    return style
