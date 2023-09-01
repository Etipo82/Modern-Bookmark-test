import sqlite3
import customtkinter
import tkinter as tk
from tkinter import *
from tkinter import ttk
import webbrowser

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

conn = sqlite3.connect("bookmarks.db")

# Create a bookmarks table
conn.execute("""
    CREATE TABLE IF NOT EXISTS bookmarks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        url TEXT NOT NULL,
        tags TEXT
    )
""")

conn.commit()
conn.close()


class MyEntryFrame(customtkinter.CTkFrame):
    def __init__(self, master, submit_callback):
        super().__init__(master)

        self.entry_title = customtkinter.CTkEntry(self, placeholder_text="Site Name")
        self.entry_title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
        self.entry_url = customtkinter.CTkEntry(self, placeholder_text="URL")
        self.entry_url.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="w")
        self.entry_tags = customtkinter.CTkEntry(self, placeholder_text="Tags")
        self.entry_tags.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="w")
        
        self.submit_button = customtkinter.CTkButton(self, text="submit", command=submit_callback)
        self.submit_button.grid(row=3, column=0, padx=10, pady=10, sticky="w")


class MySearchBox(customtkinter.CTkFrame):
    def __init__(self, master, search_callback):
        super().__init__(master)

        self.search = customtkinter.CTkEntry(self, placeholder_text="Search Database")
        self.search.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="e")
        
        self.search_button = customtkinter.CTkButton(self, text="search", command=search_callback)
        self.search_button.grid(row=1, column=0, padx=10, pady=10, sticky="e")


class ScrollableResultsFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        #self.grid_columnconfigure(0, weight=1)  # Make the inner frame expand with scrolling

    def display_results(self, result):
        # Clear any existing widgets
        for widget in self.winfo_children():
            widget.destroy()

        # Add buttons for each search result
        for row in result:
            title, url, _, _ = row
            button = customtkinter.CTkButton(self, text=title, command=lambda u=url: self.open_url(u))
            button.pack(padx=10, pady=10, fill="x")

    def open_url(self, url):
        webbrowser.open(url)


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Bookmark DB")
        self.geometry("500x350")
        self.grid_columnconfigure(0, weight=1)
        #self.grid_columnconfigure(2, weight=1)
        #self.grid_columnconfigure(3, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.entry_frame = MyEntryFrame(self, self.submit_callback)
        self.entry_frame.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="nsw")

        self.search_frame = MySearchBox(self, self.search_callback)
        self.search_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsw")

        self.scrollable_results_frame = ScrollableResultsFrame(self)
        self.scrollable_results_frame.grid(row=0, column=1, padx=10, pady=(10, 0), sticky="ns")

    def submit_callback(self):
        title = self.entry_frame.entry_title.get()
        url = self.entry_frame.entry_url.get()
        tags = self.entry_frame.entry_tags.get().split(",")  # Split the input into a list of tags

        conn = sqlite3.connect("bookmarks.db")
        tags_str = ",".join(tags)
        conn.execute("INSERT INTO bookmarks (title, url, tags) VALUES (?, ?, ?)", (title, url, tags_str))
        conn.commit()
        conn.close()

        self.entry_frame.entry_title.delete(0, tk.END)
        self.entry_frame.entry_url.delete(0, tk.END)
        self.entry_frame.entry_tags.delete(0, tk.END)


    def search_callback(self):
        tags = self.search_frame.search.get()

        conn = sqlite3.connect("bookmarks.db")
        cursor = conn.execute("SELECT title, url, tags, id FROM bookmarks WHERE tags LIKE ?", ('%' + tags + '%',))

        result = cursor.fetchall()

        self.scrollable_results_frame.display_results(result)  # Populate the scrollable frame with search results

        conn.close()


app = App()
app.mainloop()
