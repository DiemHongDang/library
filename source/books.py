import os, qrcode
from tkinter import messagebox, simpledialog
from db_init import get_db, audit

ASSET_DIR = "assets"
if not os.path.exists(ASSET_DIR):
    os.makedirs(ASSET_DIR)

def add_book(user_id, parent):
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
        audit(user_id, "add_book", isbn, title)
        img = qrcode.make(isbn)
        img.save(os.path.join(ASSET_DIR, f"{isbn}.png"))
        messagebox.showinfo("Saved", "Book added & QR generated!")

def delete_book(user_id, isbn):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM books WHERE isbn=?", (isbn,))
    conn.commit()
    conn.close()
    audit(user_id, "delete_book", isbn)

def search_book(isbn):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT title,author,location,available FROM books WHERE isbn=?", (isbn,))
    row = c.fetchone()
    conn.close()
    return row
