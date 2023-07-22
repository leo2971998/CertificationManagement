# gui.py
import os
import sqlite3
import sys
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
from ttkthemes import ThemedTk
from data_scraping import scrape_and_store  # Import the scraping function



def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
def fetch_data():
    conn = sqlite3.connect(resource_path('certifications.db'))
    c = conn.cursor()

    c.execute("SELECT * FROM certifications")
    rows = c.fetchall()

    conn.close()

    return rows


def update_data(id, owned):
    conn = sqlite3.connect('certifications.db')
    c = conn.cursor()

    c.execute("UPDATE certifications SET owned = ? WHERE id = ?", (owned, id))
    conn.commit()

    conn.close()


def load_data(owned_only=False):
    data = fetch_data()

    if owned_only:
        data = [row for row in data if row[3] == 1]

    level_dict = {1: 'Fundamentals', 2: 'Associate', 3: 'Expert', 'Specialty': 'Specialty'}

    fundamentals = [row for row in data if level_dict[row[2]] == 'Fundamentals']
    associate = [row for row in data if level_dict[row[2]] == 'Associate']
    expert = [row for row in data if level_dict[row[2]] == 'Expert']
    specialty = [row for row in data if level_dict[row[2]] == 'Specialty']

    return {
        'Fundamentals': fundamentals,
        'Associate': associate,
        'Expert': expert,
        'Specialty': specialty
    }


def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()


def load_certifications(frame, owned_only=False):
    clear_frame(frame)

    data = load_data(owned_only)

    width = frame.winfo_width() / 4

    images = []

    for idx, (category, certs) in enumerate(data.items()):
        x_pos = idx * width
        Label(frame, text=category, font=("Times New Roman", 30)).place(x=x_pos, y=50)

        # Load image after placing the Label in the frame
        img = Image.open(resource_path(f"images/{category.lower()}.png"))  # Path updated here
        img = img.resize((200, 200), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        images.append(photo)  # keep a reference to prevent garbage collection

        image_label = Label(frame)
        image_label.image = photo  # keep a reference to prevent garbage collection
        image_label.configure(image=photo)
        image_label.place(x=x_pos, y=100)

        y_pos = 350
        if owned_only:
            level_dict = {1: 'Fundamentals', 2: 'Associate', 3: 'Expert', 'Specialty': 'Specialty'}
            total = len([cert for cert in fetch_data() if level_dict[cert[2]] == category])
            owned = len(certs)
            percentage = (owned / total) * 100 if total != 0 else 0

            # Create Progress Bar
            progress = ttk.Progressbar(frame, length=150, mode='determinate', maximum=100, value=percentage)
            progress.place(x=x_pos, y=y_pos)
            Label(frame, text=f"{percentage:.2f}%", font=("Times New Roman", 11)).place(x=x_pos + 170, y=y_pos)
            y_pos += 30

        for cert in certs:
            text = f"{cert[1]} ({cert[4]})"
            var = BooleanVar(value=cert[3])
            cbutton = Checkbutton(frame, text=text, variable=var, font=("Times New Roman", 10),
                                  command=lambda cert=cert, var=var: update_data(cert[0], var.get()))
            cbutton.place(x=x_pos, y=y_pos)
            y_pos += 30


root = ThemedTk(theme="breeze")
root.geometry('1920x1080')

# Set window title
root.title("Certifications Management System")
root.iconbitmap(resource_path('images/icon.ico'))

Button(root, text="Import Data", command=scrape_and_store).place(x=0, y=0)
Button(root, text="Show All", command=lambda: load_certifications(frame, False)).place(x=100, y=0)
Button(root, text="Show Owned", command=lambda: load_certifications(frame, True)).place(x=200, y=0)

frame = Frame(root, width=1920, height=1080)
frame.place(x=0, y=60)

root.update()  # Update the root window before placing the certifications
load_certifications(frame)

root.mainloop()
