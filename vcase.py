import sqlite3
import os
import shutil
import re
import tkinter as tk
from tkinter import *
from tkinter.tix import *
from tkinter.filedialog import askopenfilename, askdirectory

#Create Window
window = tk.Tk()
window.title("V-CASE Reorganizer")

#Class for scrollable frame, not really needed
class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

frame = ScrollableFrame(window)

#Add Some Text to the window
label = tk.Label(frame.scrollable_frame, text="V-Case Reorganizer")
label.pack()

#Add Some Text to the window
label2 = tk.Label(frame.scrollable_frame, text="Select your V-Case folder")
label2.pack()

#Add a button to the window
button1 = tk.Button(
    text="Choose V-Case Folder",
    master=frame.scrollable_frame,
    width=25,
    height=5,
    bg="blue",
    fg="yellow",
)
button1.pack()

#Add Some Text to the window
label3 = tk.Label(frame.scrollable_frame, text="Select your Gemini sqlite bd file")
label3.pack()

#Add a button to the window
button2 = tk.Button(
    text="Select Database and Run",
    master=frame.scrollable_frame,
    width=25,
    height=5,
    bg="blue",
    fg="yellow",
)
button2.pack()

musicdir = False
filepath = False

#File open
def open_dir(event):
    global musicdir
    musicdir = askdirectory()
    if not musicdir:
        musicdir = False
        return

#File open
def open_file(event):
    global filepath
    global musicdir
    filepath = askopenfilename(
        filetypes=[("Database", "gemini_bd.sqlite"), ("All Files", "*.*")]
    )
    if not filepath:
        filepath = False
        return
    if not musicdir:
        print("No musicdir")
        return
    
    #SQLite Setup
    conn = sqlite3.connect(filepath)
    c = conn.cursor()
    
    #Find Missing Genres
    for row in c.execute('SELECT genre, sync_path, absolute_path, id FROM outer_table where genre IS NULL'):
        genre = "Uncategorized"
        filename = row[1]
        path = row[2]
        id = row[3]
        path = musicdir + "/" + genre
        orig_file = musicdir + "/" + filename
        new_file = musicdir + "/" + genre + "/" + filename
        new_sql_file = "/V-CASE/" + genre + "/" + filename 
        if not os.path.isdir(path):
            os.mkdir(path)
        shutil.move(orig_file, new_file)
        sql = "UPDATE outer_table SET absolute_path = ? where id = ?" 
        cur = conn.cursor()
        cur.execute(sql, (new_sql_file, id))
        conn.commit()

    #Process Remaining Genres
    for row in c.execute('SELECT genre, sync_path, absolute_path, id FROM outer_table where genre IS NOT NULL'):
        genre = row[0]
        genre = genre.replace("&", "and")
        genre = re.sub(r'[^a-zA-Z-_0-9]+', "_", genre)
        filename = row[1]
        path = row[2]
        id = row[3]
        path = musicdir + "/" + genre
        orig_file = musicdir + "/" + filename
        new_file = musicdir + "/" + genre + "/" + filename
        new_sql_file = "/V-CASE/" + genre + "/" + filename 
        if not os.path.isdir(path):
            os.mkdir(path)
        shutil.move(orig_file, new_file)
        sql = "UPDATE outer_table SET absolute_path = ? where id = ?" 
        cur = conn.cursor()
        cur.execute(sql, (new_sql_file, id))
        conn.commit()
    
    #Add Some Text to the window
    label4 = tk.Label(frame.scrollable_frame, text="Completed")
    label4.pack()

    #Process Other Genres
    for row in c.execute('SELECT genre, sync_path, absolute_path, id FROM outer_table where genre IS NOT NULL'):
        genre = row[0]
        filename = row[1]
        path = row[2]
        id = row[3]
    

button1.bind("<Button-1>", open_dir)
button2.bind("<Button-1>", open_file)

frame.pack()
window.mainloop()