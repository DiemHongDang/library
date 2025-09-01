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

def apply_theme(master, title="Library App", width=900, height=600):
    """Áp dụng style business + background"""
    master.title(title)
    master.geometry(f"{width}x{height}")
    master.resizable(True, True)

    # style business sáng (flatly = xanh dương sáng, có thể đổi thành cosmo, lumen,...)
    style = tb.Style("flatly")

    # căn giữa cửa sổ
    screen_width = master.winfo_screenwidth()
    screen_height = master.winfo_screenheight()
    x_cordinate = int((screen_width / 2) - (width / 2))
    y_cordinate = int((screen_height / 2) - (height / 2))
    master.geometry(f"{width}x{height}+{x_cordinate}+{y_cordinate}")

    # ===== Background =====
    try:
        bg_img = Image.open("image/logo.png").resize((screen_width, screen_height))
        bg_img = bg_img.convert("RGBA")

        # Làm mờ nhẹ
        alpha = 100
        for y in range(bg_img.size[1]):
            for x in range(bg_img.size[0]):
                r, g, b, a = bg_img.getpixel((x, y))
                bg_img.putpixel((x, y), (r, g, b, alpha))

        bg_photo = ImageTk.PhotoImage(bg_img)
        bg_label = tb.Label(master, image=bg_photo)
        bg_label.image = bg_photo  # giữ tham chiếu tránh bị GC
        bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)
    except Exception as e:
        print("⚠️ Không load được background:", e)

    return style
