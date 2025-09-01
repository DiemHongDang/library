from tkinter import messagebox, simpledialog
from db_init import get_db, audit

def borrow_book(user_id):
    isbn = simpledialog.askstring("Borrow", "Enter ISBN:")
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id,available FROM books WHERE isbn=?", (isbn,))
    book = c.fetchone()
    if not book:
        return messagebox.showerror("Error", "Book not found")
    if book[1] == 0:
        return messagebox.showerror("Error", "Not available")
    c.execute("INSERT INTO borrows(user_id,book_id) VALUES (?,?)", (user_id, book[0]))
    c.execute("UPDATE books SET available=0 WHERE id=?", (book[0],))
    conn.commit()
    conn.close()
    audit(user_id, "borrow", isbn)
    messagebox.showinfo("OK", "Borrowed!")

def return_book(user_id):
    isbn = simpledialog.askstring("Return", "Enter ISBN:")
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id FROM books WHERE isbn=?", (isbn,))
    book = c.fetchone()
    if not book:
        return messagebox.showerror("Error", "Book not found")
    c.execute("UPDATE books SET available=1 WHERE id=?", (book[0],))
    c.execute("UPDATE borrows SET returned_at=CURRENT_TIMESTAMP WHERE book_id=? AND returned_at IS NULL", (book[0],))
    conn.commit()
    conn.close()
    audit(user_id, "return", isbn)
    messagebox.showinfo("OK", "Returned!")
