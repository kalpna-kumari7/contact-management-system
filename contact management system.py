from tkinter import *
from tkinter import ttk, messagebox
import sqlite3
import csv

root = Tk()
root.title("Contact Manager")
root.geometry("1100x650")
root.config(bg="#f5f7fa")

# VARIABLES
FIRSTNAME = StringVar()
LASTNAME = StringVar()
GENDER = StringVar()
AGE = StringVar()
ADDRESS = StringVar()
CONTACT = StringVar()
search_var = StringVar()

selected_id = None

# -------------------- DB --------------------
def Database():
    conn = sqlite3.connect("contact.db")
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS member(
        mem_id INTEGER PRIMARY KEY AUTOINCREMENT,
        firstname TEXT, lastname TEXT, gender TEXT,
        age TEXT, address TEXT, contact TEXT)""")

    tree.delete(*tree.get_children())

    cursor.execute("SELECT * FROM member ORDER BY lastname ASC")
    for row in cursor.fetchall():
        tree.insert('', 'end', values=row)

    conn.close()
    UpdateCount()

# -------------------- ADD --------------------
def SubmitData():
    if FIRSTNAME.get() == "" or LASTNAME.get() == "":
        messagebox.showwarning("Error", "Fill required fields")
        return

    if not CONTACT.get().isdigit() or len(CONTACT.get()) != 10:
        messagebox.showerror("Error", "Enter valid 10-digit number")
        return

    conn = sqlite3.connect("contact.db")
    cursor = conn.cursor()

    cursor.execute("INSERT INTO member VALUES(NULL,?,?,?,?,?,?)",
                   (FIRSTNAME.get(), LASTNAME.get(), GENDER.get(),
                    AGE.get(), ADDRESS.get(), CONTACT.get()))

    conn.commit()
    conn.close()

    Database()
    form.destroy()

# -------------------- UPDATE --------------------
def UpdateData():
    if not selected_id:
        return

    conn = sqlite3.connect("contact.db")
    cursor = conn.cursor()

    cursor.execute("""UPDATE member SET firstname=?, lastname=?, gender=?,
                      age=?, address=?, contact=? WHERE mem_id=?""",
                   (FIRSTNAME.get(), LASTNAME.get(), GENDER.get(),
                    AGE.get(), ADDRESS.get(), CONTACT.get(), selected_id))

    conn.commit()
    conn.close()

    Database()
    form.destroy()

# -------------------- DELETE --------------------
def DeleteData():
    selected = tree.focus()
    if not selected:
        messagebox.showwarning("Error", "Select record first")
        return

    data = tree.item(selected)['values']

    if messagebox.askyesno("Confirm", "Delete this contact?"):
        conn = sqlite3.connect("contact.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM member WHERE mem_id=?", (data[0],))
        conn.commit()
        conn.close()
        Database()

# -------------------- SEARCH --------------------
def SearchData():
    keyword = search_var.get()

    conn = sqlite3.connect("contact.db")
    cursor = conn.cursor()

    query = "SELECT * FROM member WHERE firstname LIKE ? OR lastname LIKE ?"
    cursor.execute(query, ('%'+keyword+'%', '%'+keyword+'%'))

    tree.delete(*tree.get_children())
    for row in cursor.fetchall():
        tree.insert('', 'end', values=row)

    conn.close()

# -------------------- EXPORT --------------------
def ExportCSV():
    conn = sqlite3.connect("contact.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM member")

    with open("contacts.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["ID","First","Last","Gender","Age","Address","Contact"])
        writer.writerows(cursor.fetchall())

    conn.close()
    messagebox.showinfo("Success", "Exported to contacts.csv")

# -------------------- COUNT --------------------
def UpdateCount():
    conn = sqlite3.connect("contact.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM member")
    count = cursor.fetchone()[0]
    count_label.config(text=f"Total Contacts: {count}")
    conn.close()

# -------------------- EDIT --------------------
def EditSelected():
    selected = tree.focus()
    if not selected:
        messagebox.showwarning("Error", "Select record first")
        return

    data = tree.item(selected)['values']

    global selected_id
    selected_id = data[0]

    FIRSTNAME.set(data[1])
    LASTNAME.set(data[2])
    GENDER.set(data[3])
    AGE.set(data[4])
    ADDRESS.set(data[5])
    CONTACT.set(data[6])

    open_form(True)

# -------------------- CLEAR --------------------
def ClearFields():
    FIRSTNAME.set("")
    LASTNAME.set("")
    GENDER.set("")
    AGE.set("")
    ADDRESS.set("")
    CONTACT.set("")

# -------------------- FORM --------------------
def open_form(edit=False):
    global form

    form = Toplevel(root)
    form.geometry("420x450")
    form.config(bg="white")
    form.title("Contact Form")

    Label(form, text="Contact Details", font=("Segoe UI", 16, "bold"),
          bg="white").pack(pady=15)

    card = Frame(form, bg="#f9fafc", bd=1, relief=SOLID)
    card.pack(padx=20, pady=10, fill=BOTH, expand=True)

    fields = [
        ("First Name", FIRSTNAME),
        ("Last Name", LASTNAME),
        ("Age", AGE),
        ("Address", ADDRESS),
        ("Contact", CONTACT)
    ]

    for i, (text, var) in enumerate(fields):
        Label(card, text=text, bg="#f9fafc").grid(row=i, column=0, padx=10, pady=8)
        Entry(card, textvariable=var).grid(row=i, column=1, padx=10)

    Label(card, text="Gender", bg="#f9fafc").grid(row=5, column=0)
    Radiobutton(card, text="Male", variable=GENDER, value="Male", bg="#f9fafc").grid(row=5, column=1, sticky="w")
    Radiobutton(card, text="Female", variable=GENDER, value="Female", bg="#f9fafc").grid(row=5, column=1)

    if edit:
        Button(form, text="Update", bg="#f39c12", fg="white",
               width=20, command=UpdateData).pack(pady=10)
    else:
        Button(form, text="Save", bg="#2ecc71", fg="white",
               width=20, command=SubmitData).pack(pady=10)

    Button(form, text="Clear", command=ClearFields).pack()

# -------------------- STYLE --------------------
style = ttk.Style()
style.theme_use("default")

# -------------------- HEADER --------------------
header = Frame(root, bg="#2c3e50", height=60)
header.pack(fill=X)

Label(header, text="📇 Contact Manager",
      fg="white", bg="#2c3e50",
      font=("Segoe UI", 18, "bold")).pack(pady=10)

# -------------------- MAIN --------------------
main = Frame(root, bg="#f5f7fa")
main.pack(fill=BOTH, expand=True)

# SIDEBAR
sidebar = Frame(main, bg="#34495e", width=220)
sidebar.pack(side=LEFT, fill=Y)

Button(sidebar, text="➕ Add Contact", bg="#1abc9c", fg="white",
       width=18, command=lambda: open_form(False)).pack(pady=10)

Button(sidebar, text="✏️ Edit", bg="#f39c12", fg="white",
       width=18, command=EditSelected).pack(pady=10)

Button(sidebar, text="🗑 Delete", bg="#e74c3c", fg="white",
       width=18, command=DeleteData).pack(pady=10)

Button(sidebar, text="📤 Export CSV", bg="#9b59b6", fg="white",
       width=18, command=ExportCSV).pack(pady=10)

# CONTENT
content = Frame(main, bg="white")
content.pack(side=RIGHT, fill=BOTH, expand=True, padx=15, pady=15)

# SEARCH
search_frame = Frame(content, bg="black" )
search_frame.pack(fill=X)

Entry(search_frame, textvariable=search_var).pack(side=LEFT, padx=5, fill=X, expand=True)
Button(search_frame, text="Search", command=SearchData).pack(side=RIGHT, fill=X)
Button(search_frame, text="Refresh", command=Database).pack(side=RIGHT, fill=X)

# COUNT
count_label = Label(content, text="", bg="white")
count_label.pack(anchor="e")

# TABLE
tree = ttk.Treeview(content,
    columns=("ID","First","Last","Gender","Age","Address","Contact"),
    show="headings")

for col in ("ID","First","Last","Gender","Age","Address","Contact"):
    tree.heading(col, text=col)
    tree.column(col, width=120)

tree.pack(fill=BOTH, expand=True)

# INIT
Database()
root.mainloop()
