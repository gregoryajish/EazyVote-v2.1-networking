from tkinter import *
import tkinter
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tkinter.font as TkFont
from PIL import Image, ImageTk
import mysql.connector
import mysql.connector.plugins.mysql_native_password
import mysql.connector.plugins.caching_sha2_password
import os
import json
import csv

import sys

def get_script_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def get_path(rel_path):
    if not rel_path:
        return rel_path
    if os.path.isabs(rel_path):
        if os.path.exists(rel_path):
            return rel_path
        # Fallback: check if the file exists in the script directory
        fallback = os.path.join(get_script_dir(), os.path.basename(rel_path))
        if os.path.exists(fallback):
            return fallback
        return rel_path
    return os.path.join(get_script_dir(), rel_path)


def load_db_config():
    db_settings = {
        "db_host": "localhost",
        "db_user": "root",
        "db_password": "1234",
        "db_name": "vimalagiri2026"
    }
    config_path = get_path("start_screen_config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                for key in db_settings:
                    if key in config_data:
                        db_settings[key] = config_data[key]
        except Exception as e:
            print(f"Error loading db config: {e}")
    return db_settings


import sqlite3

def init_local_db():
    sqlite_path = get_path("local_voting.db")
    try:
        lite_con = sqlite3.connect(sqlite_path)
        lite_cur = lite_con.cursor()
        lite_cur.execute("CREATE TABLE IF NOT EXISTS candidate (Serial_No INTEGER PRIMARY KEY, Name TEXT, class TEXT, Post TEXT)")
        lite_cur.execute("CREATE TABLE IF NOT EXISTS votes (Serial_No INTEGER PRIMARY KEY, Name TEXT, votes INTEGER)")
        lite_cur.execute("CREATE TABLE IF NOT EXISTS offline_votes (id INTEGER PRIMARY KEY AUTOINCREMENT, Serial_No INTEGER, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
        
        lite_cur.execute("SELECT COUNT(*) FROM candidate")
        count = lite_cur.fetchone()[0]
        if count == 0:
            default_candidates = [
                (1, "Lious Basil Joshy", "XII A", "Head Boy"),
                (2, "Daniel Saji", "XI A", "Head Boy"),
                (3, "Meera P V", "XII C", "Head Girl"),
                (4, "Aida Jojo", "XI B", "Head Girl"),
                (5, "Noha Binil", "XII A", "Sports Boy"),
                (6, "Abhinav Krishna P", "XI A", "Sports Boy"),
                (7, "Abhinaya Suresh", "XII B", "Sports Girl"),
                (8, "Delna Mariya Jaison", "XI B", "Sports Girl"),
                (9, "Naveen T.S", "XII A", "Arts Boy"),
                (10, "Chris Ullas", "XI B", "Arts Boy"),
                (11, "Krishnanandha P.S", "XII B", "Arts Girl"),
                (12, "Aagna Maria Sabu", "XI B", "Arts Girl"),
                (13, "Adith Anuraj", "XII A", "Discipline Boy"),
                (14, "Geevarghese Basil", "XI A", "Discipline Boy"),
                (15, "Annmaria Ashly", "XII B", "Discipline Girl"),
                (16, "Dilsha Nasrin", "XI B", "Discipline Girl")
            ]
            for c in default_candidates:
                lite_cur.execute("INSERT OR REPLACE INTO candidate (Serial_No, Name, class, Post) VALUES (?, ?, ?, ?)", c)
                lite_cur.execute("INSERT OR REPLACE INTO votes (Serial_No, Name, votes) VALUES (?, ?, 0)", (c[0], c[1]))
            print("Pre-populated local SQLite database with default candidate list.")
        lite_con.commit()
        lite_con.close()
    except Exception as e:
        print(f"Error initializing local SQLite database in result: {e}")

def check_sqlite_valid():
    init_local_db()
    sqlite_path = get_path("local_voting.db")
    try:
        lite_con = sqlite3.connect(sqlite_path)
        lite_cur = lite_con.cursor()
        lite_cur.execute("SELECT COUNT(*) FROM candidate")
        count = lite_cur.fetchone()[0]
        lite_con.close()
        return count == 16
    except Exception:
        return False

def sync_mysql_to_sqlite(mysql_cursor):
    try:
        mysql_cursor.execute("SELECT Serial_No, Name, class, Post FROM candidate ORDER BY Serial_No ASC")
        mysql_candidates = mysql_cursor.fetchall()
        
        mysql_cursor.execute("SELECT Serial_No, Name, votes FROM votes ORDER BY Serial_No ASC")
        mysql_votes = mysql_cursor.fetchall()
        
        sqlite_path = get_path("local_voting.db")
        lite_con = sqlite3.connect(sqlite_path)
        lite_cur = lite_con.cursor()
        
        for c in mysql_candidates:
            lite_cur.execute("INSERT OR REPLACE INTO candidate (Serial_No, Name, class, Post) VALUES (?, ?, ?, ?)", c)
            
        for v in mysql_votes:
            lite_cur.execute("INSERT OR REPLACE INTO votes (Serial_No, Name, votes) VALUES (?, ?, ?)", v)
            
        lite_con.commit()
        lite_con.close()
        print("Successfully synced candidate database structure and votes from MySQL to SQLite cache.")
    except Exception as e:
        print(f"Warning: Failed to sync MySQL schema to local SQLite cache: {e}")

def sync_offline_votes():
    global cnx, cursor
    sqlite_path = get_path("local_voting.db")
    if not os.path.exists(sqlite_path):
        return
    try:
        lite_con = sqlite3.connect(sqlite_path)
        lite_cur = lite_con.cursor()
        lite_cur.execute("SELECT id, Serial_No FROM offline_votes")
        rows = lite_cur.fetchall()
        if not rows:
            lite_con.close()
            return
            
        print(f"Found {len(rows)} unsynced offline votes. Attempting to sync...")
        cnx.ping(reconnect=True, attempts=3, delay=1)
        
        synced_ids = []
        for row_id, serial_no in rows:
            try:
                cursor.execute("UPDATE votes SET votes = votes + 1 WHERE serial_no = " + str(serial_no))
                synced_ids.append(row_id)
            except mysql.connector.Error as err:
                print(f"Failed to sync vote ID {row_id} for serial {serial_no}: {err}")
                break
                
        if synced_ids:
            placeholders = ",".join("?" for _ in synced_ids)
            lite_cur.execute(f"DELETE FROM offline_votes WHERE id IN ({placeholders})", synced_ids)
            lite_con.commit()
            cnx.commit()
            print(f"Successfully synced {len(synced_ids)} offline votes to MySQL.")
            
        lite_con.close()
    except Exception as e:
        print(f"Error during offline votes syncing: {e}")

is_offline_mode = False
show_offline_warning = False
db_config = load_db_config()

try:
    cnx = mysql.connector.connect(user=db_config["db_user"], password=db_config["db_password"], host=db_config["db_host"], database=db_config["db_name"], connection_timeout=2)
    cursor = cnx.cursor()
    
    # Verify candidates table has exactly 16 entries in MySQL
    cursor.execute("Select count(*) from candidate")
    count = cursor.fetchone()[0]
    if count != 16:
        import tkinter as tk
        from tkinter import messagebox
        root_err = tk.Tk()
        root_err.withdraw()
        messagebox.showerror("Database Initialization Error", f"Database table 'candidate' has {count} candidates, but exactly 16 candidates are expected.\n\nPlease run 'sqltable.py' first to initialize the database.")
        cnx.close()
        import sys
        sys.exit(1)
        
    # Sync MySQL tables to local SQLite cache
    sync_offline_votes()
    sync_mysql_to_sqlite(cursor)
    
    # Query MySQL database directly
    cursor.execute("Select Serial_No, Name, votes from votes order by Serial_No ASC")
    votes = cursor.fetchall()
    
    cursor.execute("Select class, post from candidate order by Serial_No ASC")
    candidates = cursor.fetchall()
    
except Exception as e:
    try:
        with open(get_path("db_error.log"), "a", encoding="utf-8") as f:
            import datetime
            f.write(f"[{datetime.datetime.now()}] [result] Connection Error: {e}\n")
    except:
        pass
    print(f"Failed to connect or query MySQL database: {e}")
    # Fallback to local SQLite cache
    if check_sqlite_valid():
        is_offline_mode = True
        show_offline_warning = True
        print("Running in Offline Mode (using local cache).")
        
        sqlite_path = get_path("local_voting.db")
        lite_con = sqlite3.connect(sqlite_path)
        lite_cur = lite_con.cursor()
        
        lite_cur.execute("Select Serial_No, Name, votes from votes order by Serial_No ASC")
        votes = lite_cur.fetchall()
        
        lite_cur.execute("Select class, post from candidate order by Serial_No ASC")
        candidates = lite_cur.fetchall()
        
        lite_con.close()
    else:
        # Both MySQL and local cache are unavailable or invalid
        import tkinter as tk
        from tkinter import messagebox
        root_err = tk.Tk()
        root_err.withdraw()
        messagebox.showerror("Database Connection Error", f"Failed to connect to the MySQL database:\n{e}\n\nAdditionally, the local database cache is empty or invalid. Please check MySQL server status or run 'sqltable.py' to initialize the database.")
        import sys
        sys.exit(1)

votetablelist=[]
candidatelist=[]
for row in votes:
    a=row[0]
    b=row[1]
    c=row[2]
    votetablelist.append([a,b,c])
for item in candidates:
    d=item[0]
    e=item[1]
    candidatelist.append([d,e])
order_indices = list(range(16))
namelist = [votetablelist[idx][1] for idx in order_indices]
total_votes = votetablelist[0][2] + votetablelist[1][2]   
voteslist = [votetablelist[idx][2] for idx in order_indices]
serialnolist = [votetablelist[idx][0] for idx in order_indices]
postlist = [candidatelist[idx][1] for idx in order_indices]
classlist = [candidatelist[idx][0] for idx in order_indices]

with open(get_path('results.csv'), 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Total No of Students who Voted",total_votes])
    writer.writerow(["Serial_No", "Candidate Name", "Class","Votes Polled"])
    for j in range(0,16):
        writer.writerow([serialnolist[j], namelist[j], classlist[j], voteslist[j]]) 



# Default fallback configuration settings
DEFAULT_CONFIG = {
    "db_host": "localhost",
    "db_user": "root",
    "db_password": "1234",
    "db_name": "vimalagiri2026",
    "school_name": "Vimalagiri Public School, Kothamangalam",
    "academic_year": "2026-27",
    "logo_path": "logo.png",
    "continue_btn_path": "continuebtn.jpg",
    "continue_btn_text": "CONTINUE TO RESULTS",
    "bg_color": "#121e2a",
    "fg_color": "#03dac6",
    "text_color": "white",
    "about_text": (
        "EazyVote represents the pinnacle of election management solutions, "
        "featuring a meticulously crafted and visually stunning user interface designed to "
        "elevate the integrity and efficiency of internal and student council elections "
        "within educational institutions. Powered by robust local databases and leveraging "
        "on-site hardware infrastructure, EazyVote guarantees unparalleled levels of security, "
        "speed, and scalability, supporting virtually unlimited concurrent users with seamless "
        "performance.\n\n"
        "Tailored to meet the precise needs of Vimalagiri Public School, Kothamangalam for the 2026-27 "
        "academic session, EazyVote redefines electoral management with its rapid deployment "
        "capabilities and real-time data synchronization. Administrators benefit from instantaneous "
        "access to live election results, presented in a streamlined and intuitive interface. "
        "This seamless integration ensures administrators can make informed decisions promptly, "
        "fostering a culture of transparency and efficiency within the institution.\n\n"
        "Moreover, EazyVote eliminates post-election delays through its agile real-time updating "
        "system, providing administrators with immediate access to comprehensive election statistics "
        "and analytics. By streamlining the reporting process and offering unparalleled data "
        "visibility, EazyVote accelerates decision-making processes and ensures timely outcomes."
    ),
    "terms_text": (
        "By accessing or using EazyVote v2.1.1, you agree to comply with these terms and conditions. "
        "You are authorized to use this software solely for its intended purpose as described in the "
        "product documentation. Any unauthorized use, reproduction, or distribution of EazyVote v2.1.1 "
        "is strictly prohibited and may result in legal action.\n\n"
        "Both Lestlin Robins and/or Gregory Ajish reserve the right to modify, suspend, or "
        "terminate access to the software at any time without prior notice. EazyVote v2.1.1 is provided "
        "\"as is\" without warranty of any kind, express or implied, including but not limited to the "
        "warranties of merchantability, fitness for a particular purpose, and non-infringement.\n\n"
        "In no event shall Lestlin Robins and/or Gregory Ajish be liable for any direct, indirect, incidental, "
        "special, or consequential damages arising out of the use or inability to use EazyVote v2.1.1, "
        "including but not limited to loss of data, loss of profits, or business interruption."
    ),
    "copyright_text": (
        "EazyVote v2.1.1, developed by Gregory Ajish and Lestlin Robins, is a sophisticated and innovative "
        "election management program designed to handle an unlimited number of concurrent users with "
        "exceptional efficiency and security. This cutting-edge software provides comprehensive features, "
        "including ballot management, real-time analytics, and secure voting protocols. Tailored to meet "
        "the specific requirements of Vimalagiri Public School, Kothamangalam, EazyVote v2.1.1 integrates state-of-the-art "
        "security measures and user-friendly interfaces to ensure a seamless election process.\n\n"
        "Any unauthorized reproduction, distribution, or modification of this software is strictly prohibited. "
        "EazyVote v2.1.1 is protected by copyright laws and international treaties."
    )
}

class StartScreen:
    def __init__(self, config_path="start_screen_config.json"):
        self.config_path = get_path(config_path)
        self.config = self.load_config()
        self.root = None
        self.logo_image_ref = None
        self.continue_image_ref = None
        self.result_status = None

    def load_config(self):
        """Loads configuration from a JSON file. Fallback to defaults if file missing or corrupt."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # Merge with default to guarantee all keys exist
                    return {**DEFAULT_CONFIG, **user_config}
            except Exception as e:
                print(f"Error loading configuration file, using defaults: {e}")
        return DEFAULT_CONFIG.copy()

    def save_config(self):
        """Saves current configuration to a JSON file."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving configuration file: {e}")

    def update_logo(self):
        """Opens a file dialog to select a new school logo image."""
        file_path = filedialog.askopenfilename(
            title="Select School Logo Image",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")]
        )
        if file_path:
            script_dir = get_script_dir()
            norm_file_path = os.path.normpath(file_path)
            norm_script_dir = os.path.normpath(script_dir)
            if norm_file_path.startswith(norm_script_dir):
                file_path = os.path.relpath(norm_file_path, norm_script_dir)
            self.config["logo_path"] = file_path
            self.save_config()
            self.reload_logo()

    def update_continue_btn(self):
        """Opens a file dialog to select a new continue button image."""
        file_path = filedialog.askopenfilename(
            title="Select Continue Button Image",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp")]
        )
        if file_path:
            script_dir = get_script_dir()
            norm_file_path = os.path.normpath(file_path)
            norm_script_dir = os.path.normpath(script_dir)
            if norm_file_path.startswith(norm_script_dir):
                file_path = os.path.relpath(norm_file_path, norm_script_dir)
            self.config["continue_btn_path"] = file_path
            self.save_config()
            self.reload_continue_btn()

    def reload_logo(self):
        """Loads and scales the logo, or shows a placeholder if loading fails."""
        logo_path = self.config["logo_path"]
        loaded = False
        
        paths_to_try = []
        if logo_path:
            paths_to_try.append(logo_path)
            paths_to_try.append(get_path(logo_path))
            if os.path.isabs(logo_path):
                paths_to_try.append(os.path.join(get_script_dir(), os.path.basename(logo_path)))
        
        for path in paths_to_try:
            if path and os.path.exists(path):
                try:
                    img = Image.open(path)
                    img = img.resize((130, 130), Image.Resampling.LANCZOS)
                    
                    # Convert to RGBA and composite over solid background to support PNG transparency
                    if img.mode != "RGBA":
                        img = img.convert("RGBA")
                    bg_color = self.config.get("bg_color", "#121e2a")
                    bg_img = Image.new("RGBA", img.size, bg_color)
                    bg_img.paste(img, (0, 0), img)
                    img = bg_img.convert("RGB")
                    
                    photo = ImageTk.PhotoImage(img)
                    self.logo_label.configure(image=photo, text="", bg=bg_color)
                    self.logo_label.image = photo
                    self.logo_image_ref = photo
                    loaded = True
                    break
                except Exception as e:
                    print(f"Failed to load logo image from {path}: {e}")
                    
        if not loaded:
            # Text fallback if logo file isn't loadable or doesn't exist
            self.logo_label.configure(
                image="",
                text="[ LOGO ]",
                font=("Google Sans", 16, "bold"),
                fg=self.config["fg_color"],
                bg=self.config["bg_color"],
                bd=2,
                relief="groove",
                padx=20,
                pady=20
            )

    def reload_continue_btn(self):
        """Loads the continue button image, or shows a styled text button fallback if loading fails."""
        btn_path = self.config["continue_btn_path"]
        loaded = False
        
        paths_to_try = []
        if btn_path:
            paths_to_try.append(btn_path)
            paths_to_try.append(get_path(btn_path))
            if os.path.isabs(btn_path):
                paths_to_try.append(os.path.join(get_script_dir(), os.path.basename(btn_path)))
        
        for path in paths_to_try:
            if path and os.path.exists(path):
                try:
                    img = Image.open(path)
                    photo = ImageTk.PhotoImage(img)
                    self.continue_btn.configure(image=photo, text="", relief="flat", bg=self.config["bg_color"])
                    self.continue_btn.image = photo
                    self.continue_image_ref = photo
                    loaded = True
                    break
                except Exception as e:
                    print(f"Failed to load continue button from {path}: {e}")
                    
        if not loaded:
            # Revert to a styled text-based button
            self.continue_btn.configure(
                image="",
                text=self.config.get("continue_btn_text", "CONTINUE TO RESULTS"),
                font=("Google Sans", 14, "bold"),
                fg="black",
                bg=self.config["fg_color"],
                activebackground=self.config["bg_color"],
                activeforeground=self.config["fg_color"],
                padx=30,
                pady=15,
                relief="raised",
                bd=3
            )

    def show_about(self):
        """Displays the 'About' popup window."""
        toplevel = tk.Toplevel(self.root, bg=self.config["bg_color"])
        toplevel.title("About EazyVote")
        toplevel.geometry("700x500")
        
        font_title = TkFont.Font(family="Google Sans", size=15, weight="bold")
        font_body = TkFont.Font(family="Google Sans", size=10, weight="normal")
        
        label1 = tk.Label(toplevel, text='EazyVote v2.1.1', font=font_title, bg=self.config["bg_color"], fg="cyan")
        label1.pack(pady=(20, 10))
        
        label2 = tk.Label(toplevel, text=self.config["about_text"], font=font_body, bg=self.config["bg_color"], fg='#93c4bf', justify=tk.LEFT, wraplength=600)
        label2.pack(padx=20, pady=10)
        
        btn_close = tk.Button(toplevel, text="Close", width=15, bg="cyan", fg="black", command=toplevel.destroy, relief="flat")
        btn_close.pack(pady=20)

    def show_terms(self):
        """Displays the 'Terms & Conditions' popup window."""
        toplevel = tk.Toplevel(self.root, bg=self.config["bg_color"])
        toplevel.title("Terms and Conditions")
        toplevel.geometry("750x650")
        
        font_title = TkFont.Font(family="Google Sans", size=15, weight="bold")
        font_body = TkFont.Font(family="Google Sans", size=10, weight="normal")
        
        label1 = tk.Label(toplevel, text='Terms and Conditions', font=font_title, bg=self.config["bg_color"], fg="cyan")
        label1.pack(pady=(20, 10))
        
        label2 = tk.Label(toplevel, text=self.config["terms_text"], font=font_body, bg=self.config["bg_color"], fg='#93c4bf', justify=tk.LEFT, wraplength=650)
        label2.pack(padx=20, pady=10)
        
        label3 = tk.Label(toplevel, text='Copyright Notice', font=font_title, bg=self.config["bg_color"], fg='cyan')
        label3.pack(pady=(20, 10))
        
        copyright_text = self.config.get("copyright_text", "")
        if copyright_text:
            label4 = tk.Label(toplevel, text=copyright_text, font=font_body, bg=self.config["bg_color"], fg='#93c4bf', justify=tk.LEFT, wraplength=650)
            label4.pack(padx=20, pady=10)
        
        btn_close = tk.Button(toplevel, text="Close", width=15, bg="cyan", fg="black", command=toplevel.destroy, relief="flat")
        btn_close.pack(pady=20)

    def edit_configuration(self):
        """Opens a form window to edit school info, year, colors, and descriptions."""
        edit_window = tk.Toplevel(self.root, bg=self.config["bg_color"])
        edit_window.title("Edit Start Screen Configuration")
        edit_window.geometry("550x550")
        edit_window.grab_set()  # Make it modal
        
        tk.Label(edit_window, text="Configure Start Screen Settings", font=("Google Sans", 14, "bold"), fg="cyan", bg=self.config["bg_color"]).pack(pady=15)
        
        form_frame = tk.Frame(edit_window, bg=self.config["bg_color"])
        form_frame.pack(padx=20, fill=tk.BOTH, expand=True)
        
        # Grid Configuration
        form_frame.columnconfigure(1, weight=1)
        
        # School Name
        tk.Label(form_frame, text="School Name:", fg="white", bg=self.config["bg_color"], anchor="w").grid(row=0, column=0, sticky="ew", pady=5)
        name_var = tk.StringVar(value=self.config["school_name"])
        tk.Entry(form_frame, textvariable=name_var, width=40).grid(row=0, column=1, pady=5)
        
        # Academic Year
        tk.Label(form_frame, text="Academic Year:", fg="white", bg=self.config["bg_color"], anchor="w").grid(row=1, column=0, sticky="ew", pady=5)
        year_var = tk.StringVar(value=self.config["academic_year"])
        tk.Entry(form_frame, textvariable=year_var, width=40).grid(row=1, column=1, pady=5)
        
        # Background Color
        tk.Label(form_frame, text="Background Color (Hex):", fg="white", bg=self.config["bg_color"], anchor="w").grid(row=2, column=0, sticky="ew", pady=5)
        bg_var = tk.StringVar(value=self.config["bg_color"])
        tk.Entry(form_frame, textvariable=bg_var, width=40).grid(row=2, column=1, pady=5)
        
        # Foreground Color
        tk.Label(form_frame, text="Accent Color (Hex):", fg="white", bg=self.config["bg_color"], anchor="w").grid(row=3, column=0, sticky="ew", pady=5)
        fg_var = tk.StringVar(value=self.config["fg_color"])
        tk.Entry(form_frame, textvariable=fg_var, width=40).grid(row=3, column=1, pady=5)

        # About Description text box
        tk.Label(form_frame, text="About Text:", fg="white", bg=self.config["bg_color"], anchor="w").grid(row=4, column=0, sticky="nw", pady=5)
        about_text_box = tk.Text(form_frame, width=40, height=5)
        about_text_box.insert(tk.END, self.config["about_text"])
        about_text_box.grid(row=4, column=1, pady=5, sticky="ew")

        # Terms text box
        tk.Label(form_frame, text="Terms Text:", fg="white", bg=self.config["bg_color"], anchor="w").grid(row=5, column=0, sticky="nw", pady=5)
        terms_text_box = tk.Text(form_frame, width=40, height=5)
        terms_text_box.insert(tk.END, self.config["terms_text"])
        terms_text_box.grid(row=5, column=1, pady=5, sticky="ew")

        def save_and_apply():
            self.config["school_name"] = name_var.get()
            self.config["academic_year"] = year_var.get()
            self.config["bg_color"] = bg_var.get()
            self.config["fg_color"] = fg_var.get()
            self.config["about_text"] = about_text_box.get("1.0", tk.END).strip()
            self.config["terms_text"] = terms_text_box.get("1.0", tk.END).strip()
            
            self.save_config()
            self.apply_theme_colors()
            edit_window.destroy()

        tk.Button(edit_window, text="Save & Apply", bg="cyan", fg="black", command=save_and_apply, width=15, relief="flat").pack(pady=15)

    def apply_theme_colors(self):
        """Applies configured theme colors dynamically to the active window widgets."""
        bg = self.config["bg_color"]
        fg = self.config["fg_color"]
        text_fg = self.config["text_color"]
        
        self.root.configure(bg=bg)
        self.brand_frame.configure(bg=bg)
        self.text_frame.configure(bg=bg)
        self.school_name_label.configure(text=self.config["school_name"].upper(), fg=fg, bg=bg)
        self.election_label.configure(text=f"ELECTION RESULT {self.config['academic_year']}", fg=fg, bg=bg)
        
        self.copyright_lbl.configure(bg=bg)
        
        self.about_btn.configure(bg=bg, activebackground=bg, fg=text_fg)
        self.tc_btn.configure(bg=bg, activebackground=bg, fg=text_fg)
        
        self.reload_logo()
        self.reload_continue_btn()

    def show_context_menu(self, event):
        """Displays a right-click context menu to change images and text settings."""
        self.context_menu.post(event.x_root, event.y_root)

    def request_results_unlock(self):
        # Open a modal popup window over the start screen to ask for the PIN
        unlock_win = tk.Toplevel(self.root, bg=self.config["bg_color"])
        unlock_win.title("Supervisor Verification")
        unlock_win.geometry("350x185")
        unlock_win.resizable(False, False)
        unlock_win.grab_set()  # Make it modal
        
        # Center popup on screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_pos = (screen_width // 2) - 175
        y_pos = (screen_height // 2) - 92
        unlock_win.geometry(f"+{x_pos}+{y_pos}")
        
        tk.Label(unlock_win, text="Supervisor Unlock", font=("Google Sans", 16, "bold"), fg=self.config["fg_color"], bg=self.config["bg_color"]).pack(pady=(15, 5))
        
        # Inline error label
        error_lbl = tk.Label(unlock_win, text="", font=("Google Sans", 10), fg="#ff3b30", bg=self.config["bg_color"])
        error_lbl.pack(pady=(0, 5))
        
        pin_var = tk.StringVar()
        pin_entry = tk.Entry(unlock_win, textvariable=pin_var, show="*", font=("Google Sans", 14), width=15, justify="center", bd=1, relief="solid")
        pin_entry.pack(pady=5)
        pin_entry.focus()
        
        def check_pin(event_key=None):
            if pin_var.get() == "9744":
                unlock_win.destroy()
                self.on_continue() # Successful unlock, proceed to results dashboard
            else:
                error_lbl.configure(text="Incorrect PIN! Please try again.")
                pin_entry.delete(0, tk.END)
                
        pin_entry.bind("<Return>", check_pin)
        
        btn_frame = tk.Frame(unlock_win, bg=self.config["bg_color"])
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Unlock", command=check_pin, bg=self.config["fg_color"], fg="black", font=("Google Sans", 10), width=10, bd=0).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=unlock_win.destroy, bg="#ffb703", fg="black", font=("Google Sans", 10), width=10, bd=0).pack(side=tk.LEFT, padx=5)

    def on_continue(self):
        self.result_status = "OK"
        self.root.destroy()

    def run(self):
        self.root = tk.Tk()
        self.root.configure(bg=self.config["bg_color"])
        self.root.geometry("1366x768")
        self.root.state('zoomed')
        self.root.title("Voting - Start Screen Editor")

        font_small = TkFont.Font(family="Google Sans", size=10, weight="normal")
        
        # Branding Frame container
        self.brand_frame = tk.Frame(self.root, bg=self.config["bg_color"])
        self.brand_frame.place(relx=0.5, y=220, anchor=tk.CENTER)

        # Logo Label (Left click does nothing, Right click or Menu options updates it)
        self.logo_label = tk.Label(self.brand_frame, bg=self.config["bg_color"])
        self.logo_label.pack(side=tk.LEFT, padx=(0, 20))

        # Text container for school details
        self.text_frame = tk.Frame(self.brand_frame, bg=self.config["bg_color"])
        self.text_frame.pack(side=tk.LEFT)

        self.school_name_label = tk.Label(
            self.text_frame, 
            text=self.config["school_name"].upper(), 
            font=("Google Sans", 36, "bold"), 
            fg=self.config["fg_color"], 
            bg=self.config["bg_color"], 
            anchor=tk.CENTER
        )
        self.school_name_label.pack(fill=tk.X)

        self.election_label = tk.Label(
            self.text_frame, 
            text=f"ELECTION RESULT {self.config['academic_year']}", 
            font=("Google Sans", 26, "bold"), 
            fg=self.config["fg_color"], 
            bg=self.config["bg_color"], 
            anchor=tk.CENTER
        )
        self.election_label.pack(fill=tk.X, pady=(10, 0), padx=(0, 100))

        # Continue Button
        self.continue_btn = tk.Button(
            self.root, 
            highlightthickness=0, 
            bd=0, 
            activebackground=self.config["bg_color"], 
            bg=self.config["bg_color"], 
            cursor="hand2",
            command=self.request_results_unlock
        )
        self.continue_btn.place(relx=0.5, y=450, anchor=tk.CENTER)

        # Informational bottom bar
        self.about_btn = tk.Button(
            self.root, 
            text="ⓘ About", 
            width=20, 
            highlightthickness=0, 
            bd=0, 
            activebackground=self.config["bg_color"], 
            bg=self.config["bg_color"], 
            fg=self.config["text_color"], 
            command=self.show_about
        )
        self.about_btn.place(x=1230, y=680)

        self.tc_btn = tk.Button(
            self.root, 
            text="Terms & Conditions", 
            width=20, 
            highlightthickness=0, 
            bd=0, 
            activebackground=self.config["bg_color"], 
            bg=self.config["bg_color"], 
            fg=self.config["text_color"], 
            command=self.show_terms
        )
        self.tc_btn.place(x=1130, y=680)

        self.copyright_lbl = tk.Label(self.root, text="ⓒ 2024 EazyVote. All rights reserved.", font=font_small, fg="#6c6c6c", bg=self.config["bg_color"])
        self.copyright_lbl.place(x=562, y=680)

        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Change School Logo Image...", command=self.update_logo)
        self.context_menu.add_command(label="Change Continue Button Image...", command=self.update_continue_btn)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Edit Branding & Text Settings...", command=self.edit_configuration)

        # Note: Right-click context menu and tooltip are disabled for security during voting

        self.reload_logo()
        self.reload_continue_btn()

        self.root.mainloop()
        return self.result_status

app = StartScreen()
status = app.run()

if status == "OK":
    root= Tk()
    root.configure(bg="#121e2a")    # Setting the background of the window
    root.geometry("1366x768")    # Setting the size of the window
    root.state('zoomed')        # Maximizes the window
    root.title("Election Results")    # Setting the title of the window
    
    # Silently run in offline mode
    
    font1 = TkFont.Font(family="Google Sans",size =18)    # Setting the font
    font2 = TkFont.Font(family="Google Sans", size=11)
    font4 = TkFont.Font(family="Google Sans", size=10, weight="normal")
    font5 = TkFont.Font(family="Google Sans", size=10, weight="normal")
    font6 = TkFont.Font(family="Google Sans", size=15, weight="bold")
    
    ylist = [199.4,227.9,257.6,286.2,315,342,371,399.5,426.45,454.5,482.5,513,541.5,571,600,629]
    
    # Information in the Copyright and Terms of Conditions popup
    def clickAbout():
        toplevel = Toplevel(bg = "#121e2a")
        toplevel.title('About EazyVote')
        ABOUT_TEXT = """
        EazyVote represents the pinnacle of election management solutions, 
        featuring a meticulously crafted and visually stunning user interface designed to 
        elevate the integrity and efficiency of internal and student council elections 
        within educational institutions. Powered by robust local databases and leveraging 
        on-site hardware infrastructure, EazyVote guarantees unparalleled levels of security, 
        speed, and scalability, supporting virtually unlimited concurrent users with seamless 
        performance.
    
        Tailored to meet the precise needs of Vimalagiri Public School, Kothamangalam for the 2026-27 
        academic session, EazyVote redefines electoral management with its rapid deployment 
        capabilities and real-time data synchronization. Administrators benefit from instantaneous
        access to live election results, presented in a streamlined and intuitive interface. 
        This seamless integration ensures administrators can make informed decisions promptly, 
        fostering a culture of transparency and efficiency within the institution.
    
        Moreover, EazyVote eliminates post-election delays through its agile real-time updating 
        system, providing administrators with immediate access to comprehensive election statistics 
        and analytics. By streamlining the reporting process and offering unparalleled data 
        visibility, EazyVote accelerates decision-making processes and ensures timely outcomes.
    
        
        Last updated on: 10th July 2024"""
        label1 = Label(toplevel, text='EazyVote v2.1.1', height=0, width=30, font=font6,bg = "#121e2a",fg='cyan')
        label1.pack()
        label2 = Label(toplevel, text=ABOUT_TEXT, height=0, width=80, font=font5,bg = "#121e2a",fg='#93c4bf')
        label2.pack()
    
    def clickTerms():
        toplevel = Toplevel(bg = "#121e2a")
        toplevel.title('Terms and Conditions')
    
        termsandconditions = '''
        By accessing or using EazyVote v2.1.1, you agree to comply with these terms and conditions. 
        You are authorized to use this software solely for its intended purpose as described in the 
        product documentation. Any unauthorized use, reproduction, or distribution of EazyVote v2.1.1
        is strictly prohibited and may result in legal action.
    
        Both Lestlin Robins and/or Gregory Ajish reserve the right to modify, suspend, or
        terminate access to the software at any time without prior notice. EazyVote v2.1.1 is provided
        "as is" without warranty of any kind, express or implied, including but not limited to the 
        warranties of merchantability, fitness for a particular purpose, and non-infringement.
    
        In no event shall Lestlin Robins and/or Gregory Ajish be liable for any direct, indirect, incidental,
        special, or consequential damages arising out of the use or inability to use EazyVote v2.1.1, 
        including but not limited to loss of data, loss of profits, or business interruption.
        '''
    
        copyrightText = '''
        EazyVote v2.1.1, developed by Gregory Ajish and Lestlin Robins, is a sophisticated and innovative 
        election management program designed to handle an unlimited number of concurrent users with 
        exceptional efficiency and security. This cutting-edge software provides comprehensive features, 
        including ballot management, real-time analytics, and secure voting protocols. Tailored to meet 
        the specific requirements of Vimalagiri Public School, Kothamangalam, EazyVote v2.1.1 integrates state-of-the-art
        security measures and user-friendly interfaces to ensure a seamless election process.
    
        Any unauthorized reproduction, distribution, or modification of this software is strictly prohibited. 
        EazyVote v2.1.1 is protected by copyright laws and international treaties.'''
    
        label1 = Label(toplevel, text='Terms and Conditions', height=0, width=40,font=font6,bg = "#121e2a",fg='cyan')
        label1.pack()
        label2 = Label(toplevel, text=termsandconditions, height=0, width=100,font=font5,bg = "#121e2a",fg='#93c4bf')
        label2.pack()
        label3 = Label(toplevel, text='Copyright © 2024 EazyVote v2.1.1. All rights reserved.', height=0, width=45,font=font6,bg = "#121e2a",fg='cyan')
        label3.pack()
        label4 = Label(toplevel, text=copyrightText, height=0, width=100,font=font5,bg = "#121e2a",fg='#93c4bf')
        label4.pack()
     # Title Banner Frame at the top
    title_frame = Frame(root, bg="#121e2a")
    title_frame.pack(pady=(25, 10))
    
    school_name = app.config.get("school_name", "ST. GEORGE PUBLIC SCHOOL, KOTTAPADY").upper()
    acad_year = app.config.get("academic_year", "2026-27")
    
    # Load and scale the logo for the header
    logo_loaded = False
    logo_path = app.config.get("logo_path")
    if logo_path:
        full_logo_path = get_path(logo_path)
        if os.path.exists(full_logo_path):
            try:
                img = Image.open(full_logo_path)
                img = img.resize((60, 60), Image.Resampling.LANCZOS)
                
                # Composite over solid background to support PNG transparency
                if img.mode != "RGBA":
                    img = img.convert("RGBA")
                bg_color = "#121e2a"
                bg_img = Image.new("RGBA", img.size, bg_color)
                bg_img.paste(img, (0, 0), img)
                img = bg_img.convert("RGB")
                
                photo = ImageTk.PhotoImage(img)
                logo_label = Label(title_frame, image=photo, bg="#121e2a")
                logo_label.image = photo
                logo_label.pack(side=LEFT, padx=(0, 15))
                logo_loaded = True
            except Exception as e:
                print(f"Failed to load logo on results page: {e}")
            
    text_container = Frame(title_frame, bg="#121e2a")
    text_container.pack(side=LEFT)
    
    lbl_school = Label(text_container, text=school_name, font=("Google Sans", 20, "bold"), fg="#03dac6", bg="#121e2a", anchor="w")
    lbl_school.pack(anchor="w")
    
    lbl_title = Label(text_container, text=f"ELECTION RESULTS {acad_year}", font=("Google Sans", 13, "bold"), fg="white", bg="#121e2a", anchor="w")
    lbl_title.pack(anchor="w", pady=(2, 0))
    
    if is_offline_mode:
        lbl_offline = Label(text_container, text="⚠️ OFFLINE MODE - Showing Local Cached Results", font=("Google Sans", 11, "bold"), fg="#ff3b30", bg="#121e2a", anchor="w")
        lbl_offline.pack(anchor="w", pady=(2, 0))
    
    # Total votes card placed at the top right of the window
    votes_card = Frame(root, bg="#1a2b3c", bd=1, relief="solid", padx=20, pady=8)
    votes_card.place(relx=0.98, rely=0.03, anchor="ne")
    
    lbl_total_text = Label(votes_card, text="TOTAL STUDENTS VOTED", font=("Google Sans", 9, "bold"), fg="#93c4bf", bg="#1a2b3c")
    lbl_total_text.pack()
    
    lbl_total_val = Label(votes_card, text=total_votes, font=("Google Sans", 18, "bold"), fg="cyan", bg="#1a2b3c")
    lbl_total_val.pack()

    # Group candidates by Post
    grouped_results = {}
    for i in range(16):
        p = postlist[i]
        cand_data = {
            "sno": serialnolist[i],
            "name": namelist[i],
            "class": classlist[i],
            "votes": voteslist[i]
        }
        if p not in grouped_results:
            grouped_results[p] = []
        grouped_results[p].append(cand_data)
        
    # Sort candidates within each post by votes descending
    for p in grouped_results:
        grouped_results[p].sort(key=lambda x: x["votes"], reverse=True)
        
    post_order = [
        "Head Boy",
        "Head Girl",
        "Sports Boy",
        "Sports Girl",
        "Arts Boy",
        "Arts Girl",
        "Discipline Boy",
        "Discipline Girl"
    ]

    # Main container frame for cards - bottom pady=50 leaves plenty of space for bottom buttons
    cards_container = Frame(root, bg="#121e2a")
    cards_container.pack(pady=(10, 50), fill=BOTH, expand=True)
    
    # Configure grid weights for even distribution
    cards_container.rowconfigure(0, weight=1)
    cards_container.rowconfigure(1, weight=1)
    cards_container.rowconfigure(2, weight=1)
    cards_container.columnconfigure(0, weight=1)
    cards_container.columnconfigure(1, weight=1)
    cards_container.columnconfigure(2, weight=1)
    
    for idx, post in enumerate(post_order):
        if post not in grouped_results:
            continue
            
        r = idx // 3
        c = idx % 3
        
        # Card Frame with a modern sleek dark background and subtle border
        card = Frame(cards_container, bg="#1a2b3c", bd=1, relief="solid", padx=10, pady=5)
        card.grid(row=r, column=c, padx=10, pady=5, sticky="nsew")
        
        # Card Header (Post Name) - aligned with the card's background
        lbl_post = Label(card, text=post.upper(), font=("Google Sans", 10, "bold"), fg="#03dac6", bg="#1a2b3c", pady=2)
        lbl_post.pack(fill=X, pady=(0, 4))
        
        # Calculate max votes for this post to handle winner highlighting (and ties)
        max_votes = max(x["votes"] for x in grouped_results[post])
        category_total_votes = sum(x["votes"] for x in grouped_results[post])
        
        # Candidates list
        for cand_idx, cand in enumerate(grouped_results[post]):
            row_bg = "#1a2b3c" if cand_idx % 2 == 0 else "#22354a"
            
            # Single row frame
            row_frame = Frame(card, bg=row_bg, padx=6, pady=3)
            row_frame.pack(fill=X, pady=2)
            
            # Winner logic: highlight if they have the max votes and max votes > 0
            is_winner = (cand["votes"] == max_votes and max_votes > 0)
            name_color = "#ffb703" if is_winner else "#ffffff"
            votes_color = "#ffb703" if is_winner else "#03dac6"
            font_weight = "bold" if is_winner else "normal"
            
            name_text = f"🏆 {cand['name']}" if is_winner else cand['name']
            
            # Top line of candidate row: Name + Class on Left, Votes + Percentage on Right
            top_line = Frame(row_frame, bg=row_bg)
            top_line.pack(fill=X)
            
            lbl_name = Label(top_line, text=name_text, font=("Google Sans", 10, font_weight), fg=name_color, bg=row_bg, anchor="w")
            lbl_name.pack(side=LEFT)
            
            lbl_class = Label(top_line, text=f" ({cand['class']})", font=("Google Sans", 9), fg="#93c4bf", bg=row_bg)
            lbl_class.pack(side=LEFT)
            
            # Percentage text
            pct = 0
            if category_total_votes > 0:
                pct = int((cand["votes"] / category_total_votes) * 100)
            pct_text = f" ({pct}%)" if category_total_votes > 0 else ""
            
            lbl_votes = Label(top_line, text=f"{cand['votes']} votes{pct_text}", font=("Google Sans", 10, "bold"), fg=votes_color, bg=row_bg)
            lbl_votes.pack(side=RIGHT)
            
            # Bottom line of candidate row: Flat custom progress bar
            bar_frame = Frame(row_frame, bg=row_bg, pady=2)
            bar_frame.pack(fill=X)
            
            pct_fraction = (cand["votes"] / category_total_votes) if category_total_votes > 0 else 0.0
            
            # Visual progress bar tracks using flat frames for full responsiveness
            bar_container = Frame(bar_frame, bg="#2d3f55", height=4)
            bar_container.pack(fill=X, expand=True, pady=(2, 1))
            
            if pct_fraction > 0:
                bar_fill = Frame(bar_container, bg=votes_color, height=4)
                bar_fill.place(relx=0, rely=0, relwidth=pct_fraction, relheight=1)

    # Bottom bar placed dynamically relative to the window height
    ProductLabel = Label(root, text="ⓒ 2024 EazyVote. All rights reserved.", font=("Google Sans", 9), fg="#6c6c6c", bg="#121e2a", highlightthickness=0)
    ProductLabel.place(relx=0.5, rely=0.96, anchor=CENTER)
    
    AboutButton = Button(root, text="ⓘ About", width=15, highlightthickness=0, bd=0, activebackground="#121e2a", bg="#121e2a", fg='white', command=clickAbout)
    AboutButton.place(relx=0.92, rely=0.96, anchor=CENTER)
    
    TandCButton = Button(root, text="Terms & Conditions", width=18, highlightthickness=0, bd=0, activebackground="#121e2a", bg="#121e2a", fg='white', command=clickTerms)
    TandCButton.place(relx=0.82, rely=0.96, anchor=CENTER)
    
    root.mainloop()
   


