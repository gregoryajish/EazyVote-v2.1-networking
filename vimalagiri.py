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
                text="CONTINUE TO VOTE",
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
        self.election_label.configure(text=f"ELECTION {self.config['academic_year']}", fg=fg, bg=bg)
        
        self.copyright_lbl.configure(bg=bg)
        
        self.about_btn.configure(bg=bg, activebackground=bg, fg=text_fg)
        self.tc_btn.configure(bg=bg, activebackground=bg, fg=text_fg)
        
        # Reload images to pick up any changes in widget colors
        self.reload_logo()
        self.reload_continue_btn()

    def show_context_menu(self, event):
        """Displays a right-click context menu to change images and text settings."""
        self.context_menu.post(event.x_root, event.y_root)

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
            text=f"ELECTION {self.config['academic_year']}", 
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
            command=self.on_continue
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

        # Context Menu for configuration & updating images
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Change School Logo Image...", command=self.update_logo)
        self.context_menu.add_command(label="Change Continue Button Image...", command=self.update_continue_btn)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Edit Branding & Text Settings...", command=self.edit_configuration)

        # Note: Right-click context menu and tooltip are disabled for security during voting

        # Initial loading of images
        self.reload_logo()
        self.reload_continue_btn()

        self.root.mainloop()
        return self.result_status

x = 0
exit_unlocked = False
app = StartScreen()
status = app.run()
windstat = (status == "OK")

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
        print(f"Error initializing local SQLite database: {e}")

def check_sqlite_valid():
    sqlite_path = get_path("local_voting.db")
    if not os.path.exists(sqlite_path):
        return False
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
    lite_con = None
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
        print("Successfully synced candidate database structure and votes from MySQL to SQLite cache.")
    except Exception as e:
        print(f"Warning: Failed to sync MySQL schema to local SQLite cache: {e}")
    finally:
        if lite_con:
            try:
                lite_con.close()
            except:
                pass

def sync_offline_votes():
    global cnx, cursor
    sqlite_path = get_path("local_voting.db")
    if not os.path.exists(sqlite_path):
        return
    lite_con = None
    try:
        lite_con = sqlite3.connect(sqlite_path)
        lite_cur = lite_con.cursor()
        lite_cur.execute("SELECT id, Serial_No FROM offline_votes")
        rows = lite_cur.fetchall()
        if not rows:
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
            
    except Exception as e:
        print(f"Error during offline votes syncing: {e}")
    finally:
        if lite_con:
            try:
                lite_con.close()
            except:
                pass

is_offline_mode = False
show_offline_warning = False
db_config = load_db_config()
init_local_db()

# Create the main root window early but hide it with withdraw()
# so we can use it as parent for database warning/error popups
# and prevent PyImage / TclError resource mismatch crashes
root = Tk()
root.withdraw()
root.configure(bg="#121e2a")
root.geometry("1366x768")
root.state('zoomed')
root.attributes('-fullscreen', True)
root.protocol("WM_DELETE_WINDOW", lambda: None)
root.title("Voting")

try:
    cnx = mysql.connector.connect(user=db_config["db_user"], password=db_config["db_password"], host=db_config["db_host"], database=db_config["db_name"], connection_timeout=2)
    cursor = cnx.cursor()
    
    cursor.execute("Select count(*) from candidate")
    count = cursor.fetchone()[0]
    if count != 16:
        from tkinter import messagebox
        messagebox.showerror("Database Initialization Error", f"Database table 'candidate' has {count} candidates, but exactly 16 candidates are expected.\n\nPlease run 'sqltable.py' first to initialize the database.", parent=root)
        cnx.close()
        root.destroy()
        import sys
        sys.exit(1)
        
    # Online mode: Sync offline votes first, then update local cache
    sync_offline_votes()
    sync_mysql_to_sqlite(cursor)
    
except Exception as e:
    try:
        with open(get_path("db_error.log"), "a", encoding="utf-8") as f:
            import datetime
            f.write(f"[{datetime.datetime.now()}] [voting] Connection Error: {e}\n")
    except:
        pass
    print(f"Failed to connect or query MySQL database: {e}")
    if check_sqlite_valid():
        is_offline_mode = True
        show_offline_warning = True
        count = 16
        print("Running in Offline Mode (using local cache).")
    else:
        from tkinter import messagebox
        messagebox.showerror("Database Connection Error", f"Failed to connect to the MySQL database:\n{e}\n\nAdditionally, the local database cache is empty or invalid. Please check MySQL server status or run 'sqltable.py' to initialize the database.", parent=root)
        root.destroy()
        import sys
        sys.exit(1)


def convertTuple(tup):
    string = ''
    for item in tup:
        string = string + str(item)
    return string

# Deiconify the window now that loading and syncing is complete
if windstat == True:
    root.deiconify()
    root.focus_force()
root.protocol("WM_DELETE_WINDOW", lambda: None) # Disable Alt+F4 and close button
root.title("Voting")    # Setting the title of the window

font1 = TkFont.Font(family="Google Sans",size =14)    # Setting the font
font2 = TkFont.Font(family="Google Sans", size=25, weight="bold")
font3 = TkFont.Font(family="Google Sans", size=17, weight="normal")
font4 = TkFont.Font(family="Google Sans", size=10, weight="normal")

quitimg = Image.open(get_path("quitbtn.jpg"))
quitbtn = ImageTk.PhotoImage(quitimg)
# Load cover image first so it can be used as fallback
try:
    cover = Image.open(get_path("Candidates/cover.jpg")).resize((180, 225), Image.Resampling.LANCZOS)
    coverimg = ImageTk.PhotoImage(cover)
except Exception as e:
    print(f"Failed to load cover.jpg: {e}")
    coverimg = None

candidate_images = []
for i in range(1, count + 1):
    loaded = False
    for ext in [".jpg", ".jpeg", ".JPG", ".JPEG", ".png"]:
        path = get_path(f"Candidates/candidate{i}{ext}")
        if os.path.exists(path):
            try:
                candidate_images.append(ImageTk.PhotoImage(Image.open(path).resize((180, 225), Image.Resampling.LANCZOS)))
                loaded = True
                break
            except Exception as e:
                print(f"Failed to load {path}: {e}")
    if not loaded:
        print(f"Failed to find Candidates/candidate{i} with standard extensions, using cover fallback")
        candidate_images.append(coverimg)

# Safely assign legacy image variables to avoid index errors
candidate_images_vars = []
for idx in range(17):
    if idx < len(candidate_images):
        candidate_images_vars.append(candidate_images[idx])
    else:
        candidate_images_vars.append(coverimg)
Candidate1img, Candidate2img, Candidate3img, Candidate4img, Candidate5img, Candidate6img, Candidate7img, Candidate8img, Candidate9img, Candidate10img, Candidate11img, Candidate12img, Candidate13img, Candidate14img, Candidate15img, Candidate16img, Candidate17img = candidate_images_vars

finishimg = Image.open(get_path("finishbtn.jpg"))
finishbtn = ImageTk.PhotoImage(finishimg)
nextimg = Image.open(get_path("nextbtn.jpg"))
nextbtn = ImageTk.PhotoImage(nextimg)

def get_img_width(img):
    if img is not None:
        try:
            return img.width()
        except:
            pass
    return 200

def get_img_height(img):
    if img is not None:
        try:
            return img.height()
        except:
            pass
    return 200

if is_offline_mode:
    sqlite_path = get_path("local_voting.db")
    lite_con = sqlite3.connect(sqlite_path)
    lite_cur = lite_con.cursor()
    
    lite_cur.execute("SELECT Name FROM candidate ORDER BY Serial_No ASC")
    record = lite_cur.fetchall()
    candlist = []
    for i in record:
        candlist.append(convertTuple(i))
        
    lite_cur.execute("SELECT Serial_No FROM candidate ORDER BY Serial_No ASC")
    sernotuple = lite_cur.fetchall()
    sernolist = []
    for i in sernotuple:
        sernolist.append(str(convertTuple(i)))
        
    lite_cur.execute("SELECT class FROM candidate ORDER BY Serial_No ASC")
    classtuple = lite_cur.fetchall()
    classlist = []
    for i in classtuple:
        classlist.append(convertTuple(i))
        
    lite_con.close()
else:
    cursor.execute("Select Name from candidate order by Serial_No ASC")
    record=cursor.fetchall()
    candlist=[]
    for i in record:
        i=convertTuple(i)
        candlist.append(i)

    cursor.execute("Select Serial_NO from candidate order by Serial_No ASC")
    sernotuple = cursor.fetchall()
    sernolist=[]
    for i in sernotuple:
        i=str(convertTuple(i))
        sernolist.append(i)

    cursor.execute("Select class from candidate order by Serial_No ASC")
    classtuple = cursor.fetchall()
    classlist=[]
    for i in classtuple:
        i=convertTuple(i)
        classlist.append(i)

postlist = [
    "Head Boy",
    "Head Girl",
    "Sports Boy",
    "Sports Girl",
    "Arts Boy",
    "Arts Girl",
    "Discipline Boy",
    "Discipline Girl"
]


def execute_vote_update(serial_no):
    sqlite_path = get_path("local_voting.db")
    try:
        lite_con = sqlite3.connect(sqlite_path)
        lite_cur = lite_con.cursor()
        # 1. Update SQLite votes immediately (to keep local state accurate)
        lite_cur.execute("UPDATE votes SET votes = votes + 1 WHERE Serial_No = ?", (serial_no,))
        # 2. Queue the vote locally for later syncing to MySQL
        lite_cur.execute("INSERT INTO offline_votes (Serial_No) VALUES (?)", (serial_no,))
        lite_con.commit()
        lite_con.close()
        print(f"Recorded vote locally for candidate {serial_no} in SQLite (queued for sync).")
        return True
    except Exception as e:
        print(f"Failed to record vote locally: {e}")
        return False


def load_page_candidates(left_post_name, right_post_name, left_start_idx, left_count, right_start_idx, right_count):
    global PostLabel1, PostLabel2
    global Candidate1Btn, Candidate2Btn, Candidate3Btn, Candidate4Btn
    global Candidate1Label, Candidate2Label, Candidate3Label, Candidate4Label
    global Candidate1ClassLabel, Candidate2ClassLabel, Candidate3ClassLabel, Candidate4ClassLabel
    global testLabel1, testLabel2, testLabel3, testLabel4

    # Hide all candidate widgets first (to ensure clean slate)
    for i in range(1, 9):
        for suffix in ["Btn", "Label", "ClassLabel"]:
            name = f"Candidate{i}{suffix}"
            if name in globals() and globals()[name] is not None:
                try:
                    globals()[name].place_forget()
                except:
                    pass

    # Post Labels
    PostLabel1.configure(text=left_post_name)
    PostLabel1.place(x=345, y=80, anchor=tk.CENTER)
    
    PostLabel2.configure(text=right_post_name)
    PostLabel2.place(x=1025, y=80, anchor=tk.CENTER)

    # Configure Left column
    # Row 1 Left (Candidate 1 & 2)
    if left_count >= 1:
        testLabel1.configure(text=sernolist[left_start_idx])
        Candidate1Btn.configure(image=candidate_images[left_start_idx], state=NORMAL, command=lambda: clicked("Button 1"))
        Candidate1Label.configure(text=candlist[left_start_idx])
        Candidate1ClassLabel.configure(text=f"({classlist[left_start_idx]})")
        Candidate1Btn.place(x=125, y=140)
        Candidate1Label.place(x=215, y=385, anchor=tk.CENTER)
        Candidate1ClassLabel.place(x=215, y=410, anchor=tk.CENTER)
    
    if left_count >= 2:
        testLabel2.configure(text=sernolist[left_start_idx+1])
        Candidate2Btn.configure(image=candidate_images[left_start_idx+1], state=NORMAL, command=lambda: clicked("Button 2"))
        Candidate2Label.configure(text=candlist[left_start_idx+1])
        Candidate2ClassLabel.configure(text=f"({classlist[left_start_idx+1]})")
        Candidate2Btn.place(x=385, y=140)
        Candidate2Label.place(x=475, y=385, anchor=tk.CENTER)
        Candidate2ClassLabel.place(x=475, y=410, anchor=tk.CENTER)

    # Configure Right column
    # Row 1 Right (Candidate 3 & 4)
    if right_count >= 1:
        testLabel3.configure(text=sernolist[right_start_idx])
        Candidate3Btn.configure(image=candidate_images[right_start_idx], state=NORMAL, command=lambda: clicked1("Button 3"))
        Candidate3Label.configure(text=candlist[right_start_idx])
        Candidate3ClassLabel.configure(text=f"({classlist[right_start_idx]})")
        Candidate3Btn.place(x=805, y=140)
        Candidate3Label.place(x=895, y=385, anchor=tk.CENTER)
        Candidate3ClassLabel.place(x=895, y=410, anchor=tk.CENTER)
        
    if right_count >= 2:
        testLabel4.configure(text=sernolist[right_start_idx+1])
        Candidate4Btn.configure(image=candidate_images[right_start_idx+1], state=NORMAL, command=lambda: clicked1("Button 4"))
        Candidate4Label.configure(text=candlist[right_start_idx+1])
        Candidate4ClassLabel.configure(text=f"({classlist[right_start_idx+1]})")
        Candidate4Btn.place(x=1065, y=140)
        Candidate4Label.place(x=1155, y=385, anchor=tk.CENTER)
        Candidate4ClassLabel.place(x=1155, y=410, anchor=tk.CENTER)


def clicked(button):
    global x
    global nextBtn2, nextBtn3, nextBtn4, nextBtn5
    global testLabel1, testLabel2, testLabel5, testLabel6
    global Candidate1Btn, Candidate2Btn, Candidate5Btn, Candidate6Btn
    
    x += 1
    
    Candidate1Btn["state"] = DISABLED
    Candidate2Btn["state"] = DISABLED
    if 'Candidate5Btn' in globals() and Candidate5Btn is not None:
        try:
            Candidate5Btn["state"] = DISABLED
        except:
            pass
    if 'Candidate6Btn' in globals() and Candidate6Btn is not None:
        try:
            Candidate6Btn["state"] = DISABLED
        except:
            pass
        
    no = None
    if button == "Button 1":
        no = testLabel1.cget("text")
    elif button == "Button 2":
        no = testLabel2.cget("text")
    elif button == "Button 5":
        no = testLabel5.cget("text")
    elif button == "Button 6":
        no = testLabel6.cget("text")
        
    if no:
        if not execute_vote_update(no):
            messagebox.showerror("Database Error", "Failed to save your vote. Please try again.")
            Candidate1Btn["state"] = NORMAL
            Candidate2Btn["state"] = NORMAL
            if 'Candidate5Btn' in globals() and Candidate5Btn is not None:
                try:
                    Candidate5Btn["state"] = NORMAL
                except:
                    pass
            if 'Candidate6Btn' in globals() and Candidate6Btn is not None:
                try:
                    Candidate6Btn["state"] = NORMAL
                except:
                    pass
            x -= 1
            return
            
    if x == 2:
        nextBtn2 = tkinter.Button(root, image=nextbtn, command=lambda: nextclick2("Button 4"), highlightthickness=0, bd=0, activebackground="#121e2a")
        nextBtn2.place(x=593, y=520)
    elif x == 4:
        nextBtn3 = tkinter.Button(root, image=nextbtn, command=lambda: nextclick3("Button 4"), highlightthickness=0, bd=0, activebackground="#121e2a")
        nextBtn3.place(x=593, y=520)
    elif x == 6:
        nextBtn4 = tkinter.Button(root, image=nextbtn, command=lambda: nextclick4("Button 4"), highlightthickness=0, bd=0, activebackground="#121e2a")
        nextBtn4.place(x=593, y=520)
    elif x == 8:
        nextBtn5 = tkinter.Button(root, image=finishbtn, command=lambda: nextclick5("Button 4"), highlightthickness=0, bd=0, activebackground="#121e2a")
        nextBtn5.place(x=593, y=520)


def clicked1(button):
    global x
    global nextBtn2, nextBtn3, nextBtn4, nextBtn5
    global testLabel3, testLabel4, testLabel7, testLabel8
    global Candidate3Btn, Candidate4Btn, Candidate7Btn, Candidate8Btn
    
    x += 1
    
    Candidate3Btn["state"] = DISABLED
    Candidate4Btn["state"] = DISABLED
    if 'Candidate7Btn' in globals() and Candidate7Btn is not None:
        try:
            Candidate7Btn["state"] = DISABLED
        except:
            pass
    if 'Candidate8Btn' in globals() and Candidate8Btn is not None:
        try:
            Candidate8Btn["state"] = DISABLED
        except:
            pass
        
    no = None
    if button == "Button 3":
        no = testLabel3.cget("text")
    elif button == "Button 4":
        no = testLabel4.cget("text")
    elif button == "Button 7":
        no = testLabel7.cget("text")
    elif button == "Button 8":
        no = testLabel8.cget("text")
        
    if no:
        if not execute_vote_update(no):
            messagebox.showerror("Database Error", "Failed to save your vote. Please try again.")
            Candidate3Btn["state"] = NORMAL
            Candidate4Btn["state"] = NORMAL
            if 'Candidate7Btn' in globals() and Candidate7Btn is not None:
                try:
                    Candidate7Btn["state"] = NORMAL
                except:
                    pass
            if 'Candidate8Btn' in globals() and Candidate8Btn is not None:
                try:
                    Candidate8Btn["state"] = NORMAL
                except:
                    pass
            x -= 1
            return
            
    if x == 2:
        nextBtn2 = tkinter.Button(root, image=nextbtn, command=lambda: nextclick2("Button 4"), highlightthickness=0, bd=0, activebackground="#121e2a")
        nextBtn2.place(x=593, y=520)
    elif x == 4:
        nextBtn3 = tkinter.Button(root, image=nextbtn, command=lambda: nextclick3("Button 4"), highlightthickness=0, bd=0, activebackground="#121e2a")
        nextBtn3.place(x=593, y=520)
    elif x == 6:
        nextBtn4 = tkinter.Button(root, image=nextbtn, command=lambda: nextclick4("Button 4"), highlightthickness=0, bd=0, activebackground="#121e2a")
        nextBtn4.place(x=593, y=520)
    elif x == 8:
        nextBtn5 = tkinter.Button(root, image=finishbtn, command=lambda: nextclick5("Button 4"), highlightthickness=0, bd=0, activebackground="#121e2a")
        nextBtn5.place(x=593, y=520)


def nextclick2(button):
    global nextBtn2
    try:
        nextBtn2.destroy()
    except:
        pass
    
    # Screen 2: Sports Boy (idx 4, count 2) & Sports Girl (idx 6, count 2)
    load_page_candidates(postlist[2], postlist[3], 4, 2, 6, 2)


def nextclick3(button):
    global nextBtn3
    try:
        nextBtn3.destroy()
    except:
        pass
    
    # Screen 3: Arts Boy (idx 8, count 2) & Arts Girl (idx 10, count 2)
    load_page_candidates(postlist[4], postlist[5], 8, 2, 10, 2)


def nextclick4(button):
    global nextBtn4
    try:
        nextBtn4.destroy()
    except:
        pass
    
    # Screen 4: Discipline Boy (idx 12, count 2) & Discipline Girl (idx 14, count 2)
    load_page_candidates(postlist[6], postlist[7], 12, 2, 14, 2)


exit_unlocked = False

def on_exit_click():
    global exit_unlocked, cnx, cursor, is_offline_mode
    print(f"Exit button clicked. current exit_unlocked state: {exit_unlocked}")
    if exit_unlocked:
        exit_unlocked = False
        
        # Batch sync all accumulated votes to MySQL on screen reset
        try:
            db_config = load_db_config()
            if 'cnx' not in globals() or cnx is None:
                # Try to establish connection if we started offline
                cnx = mysql.connector.connect(
                    user=db_config["db_user"], 
                    password=db_config["db_password"], 
                    host=db_config["db_host"], 
                    database=db_config["db_name"],
                    connection_timeout=2
                )
                cursor = cnx.cursor()
                is_offline_mode = False
                print("MySQL server connection established on reset.")
            else:
                cnx.ping(reconnect=True, attempts=1, delay=0)
            
            sync_offline_votes()
            sync_mysql_to_sqlite(cursor)
        except Exception as e:
            print(f"MySQL sync skipped during reset (network offline): {e}")
            
        setup_first_screen()
    else:
        # Do absolutely nothing when clicked by the student
        pass


def exit_application(event=None):
    # Open a pop-up window to ask for the PIN to close the application entirely
    exit_win = Toplevel(root, bg="#121e2a")
    exit_win.title("Exit Application")
    exit_win.geometry("350x185")
    exit_win.resizable(False, False)
    exit_win.grab_set()  # Make it modal
    
    # Calculate position to center the popup on screen
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_pos = (screen_width // 2) - 175
    y_pos = (screen_height // 2) - 92
    exit_win.geometry(f"+{x_pos}+{y_pos}")
    
    Label(exit_win, text="Exit Application", font=font2, fg="#ffb703", bg="#121e2a").pack(pady=(15, 5))
    
    # Inline error label
    error_lbl = Label(exit_win, text="", font=font4, fg="#ff3b30", bg="#121e2a")
    error_lbl.pack(pady=(0, 5))
    
    pin_var = StringVar()
    pin_entry = Entry(exit_win, textvariable=pin_var, show="*", font=font1, width=15, justify="center", bd=1, relief="solid")
    pin_entry.pack(pady=5)
    pin_entry.focus()
    
    def check_pin(event_key=None):
        if pin_var.get() == "9744":
            exit_win.destroy()
            root.destroy()
            import sys
            sys.exit(0)
        else:
            error_lbl.configure(text="Incorrect PIN! Please try again.")
            pin_entry.delete(0, END)
            
    pin_entry.bind("<Return>", check_pin)
    
    btn_frame = Frame(exit_win, bg="#121e2a")
    btn_frame.pack(pady=10)
    
    Button(btn_frame, text="Exit", command=check_pin, bg="#ffb703", fg="black", font=font4, width=10, bd=0, activebackground="#ffb703").pack(side=LEFT, padx=5)
    Button(btn_frame, text="Cancel", command=exit_win.destroy, bg="#03dac6", fg="black", font=font4, width=10, bd=0).pack(side=LEFT, padx=5)


def verify_unlock(event=None):
    global exit_unlocked
    print("verify_unlock (key '0') pressed.")
    if 'exitbtn' in globals() and exitbtn is not None:
        exit_unlocked = True
        print("Exit button successfully UNLOCKED.")


def nextclick5(button):
    global FinishLabel1, FinishLabel2, ProductLabel
    global nextBtn5, exitbtn, exit_unlocked
    
    # Destroy all candidate widgets
    for i in range(1, 9):
        for suffix in ["Btn", "Label", "ClassLabel"]:
            name = f"Candidate{i}{suffix}"
            if name in globals() and globals()[name] is not None:
                try:
                    globals()[name].destroy()
                except:
                    pass
        test_name = f"testLabel{i}"
        if test_name in globals() and globals()[test_name] is not None:
            try:
                globals()[test_name].destroy()
            except:
                pass
                
    if "PostLabel1" in globals() and PostLabel1 is not None:
        PostLabel1.destroy()
    if "PostLabel2" in globals() and PostLabel2 is not None:
        PostLabel2.destroy()
        
    if "nextBtn2" in globals() and nextBtn2 is not None:
        try:
            nextBtn2.destroy()
        except:
            pass

    # Destroy the nextBtn5 (Finish button) widget so it doesn't linger in the background of the congratulations screen
    if "nextBtn5" in globals() and nextBtn5 is not None:
        try:
            nextBtn5.destroy()
        except:
            pass

    FinishLabel1 = Label(root, text="Congratulations! You have finished the voting procedure.", font=font2, fg="#7D6AF0", bg="#121e2a", highlightthickness=0, highlightcolor="#000000")
    FinishLabel1.place(x=240, y=190)
    FinishLabel2 = Label(root, text="Thank you for using this service.", font=font1, fg="#8899A6", bg="#121e2a", highlightthickness=0)
    FinishLabel2.place(x=535, y=250)
    
    # Display the Exit/Quit button on screen immediately, but make it do nothing when clicked by the student
    exit_unlocked = False
    exitbtn = tkinter.Button(root, image=quitbtn, command=on_exit_click, highlightthickness=0, bd=0, activebackground="#121e2a")
    exitbtn.place(x=590, y=500)
    root.focus_force()
    exitbtn.focus_force()


def setup_first_screen():
    global PostLabel1, PostLabel2
    global Candidate1Btn, Candidate2Btn, Candidate3Btn, Candidate4Btn, Candidate5Btn, Candidate6Btn, Candidate7Btn, Candidate8Btn
    global Candidate1Label, Candidate2Label, Candidate3Label, Candidate4Label, Candidate5Label, Candidate6Label, Candidate7Label, Candidate8Label
    global Candidate1ClassLabel, Candidate2ClassLabel, Candidate3ClassLabel, Candidate4ClassLabel, Candidate5ClassLabel, Candidate6ClassLabel, Candidate7ClassLabel, Candidate8ClassLabel
    global testLabel1, testLabel2, testLabel3, testLabel4, testLabel5, testLabel6, testLabel7, testLabel8
    global FinishLabel1, FinishLabel2, exitbtn, nextBtn1, nextBtn2, nextBtn3, nextBtn4, nextBtn5, label1, label2, label3, label4, exit_unlocked
    global x
    
    x = 0
    exit_unlocked = False
    
    # Clean up confirmation screen widgets by destroying them and setting variables to None
    for name in ["FinishLabel1", "FinishLabel2", "exitbtn", "nextBtn1", "nextBtn2", "nextBtn3", "nextBtn4", "nextBtn5", "label1", "label2", "label3", "label4"]:
        if name in globals():
            widget = globals()[name]
            if widget is not None:
                try:
                    widget.destroy()
                except:
                    pass
                globals()[name] = None

    # Post Labels
    PostLabel1 = Label(root, text="", font=font2, bg="#121e2a", fg="#03dac6", highlightthickness=0)
    PostLabel2 = Label(root, text="", font=font2, bg="#121e2a", fg="#03dac6", highlightthickness=0)

    # Initialize Candidate 1 to 8 widgets
    testLabel1 = Label(root, font=font1, fg="White", bg="#121e2a", highlightthickness=0)
    Candidate1Label = Label(root, font=font1, fg="White", bg="#121e2a", highlightthickness=0)
    Candidate1ClassLabel = Label(root, font=font1, fg="grey", bg="#121e2a", highlightthickness=0)
    Candidate1Btn = tkinter.Button(root, borderwidth=0, highlightthickness=0, activebackground="black")

    testLabel2 = Label(root, font=font1, fg="White", bg="#121e2a", highlightthickness=0)
    Candidate2Label = Label(root, font=font1, fg="White", bg="#121e2a", highlightthickness=0)
    Candidate2ClassLabel = Label(root, font=font1, fg="grey", bg="#121e2a", highlightthickness=0)
    Candidate2Btn = tkinter.Button(root, borderwidth=0, highlightthickness=0, activebackground="black")

    testLabel3 = Label(root, font=font1, fg="White", bg="#121e2a", highlightthickness=0)
    Candidate3Label = Label(root, font=font1, fg="White", bg="#121e2a", highlightthickness=0)
    Candidate3ClassLabel = Label(root, font=font1, fg="grey", bg="#121e2a", highlightthickness=0)
    Candidate3Btn = tkinter.Button(root, borderwidth=0, highlightthickness=0, activebackground="black")

    testLabel4 = Label(root, font=font1, fg="White", bg="#121e2a", highlightthickness=0)
    Candidate4Label = Label(root, font=font1, fg="White", bg="#121e2a", highlightthickness=0)
    Candidate4ClassLabel = Label(root, font=font1, fg="grey", bg="#121e2a", highlightthickness=0)
    Candidate4Btn = tkinter.Button(root, borderwidth=0, highlightthickness=0, activebackground="black")

    testLabel5 = Label(root, font=font1, fg="White", bg="#121e2a", highlightthickness=0)
    Candidate5Label = Label(root, font=font1, fg="White", bg="#121e2a", highlightthickness=0)
    Candidate5ClassLabel = Label(root, font=font1, fg="grey", bg="#121e2a", highlightthickness=0)
    Candidate5Btn = tkinter.Button(root, borderwidth=0, highlightthickness=0, activebackground="black")

    testLabel6 = Label(root, font=font1, fg="White", bg="#121e2a", highlightthickness=0)
    Candidate6Label = Label(root, font=font1, fg="White", bg="#121e2a", highlightthickness=0)
    Candidate6ClassLabel = Label(root, font=font1, fg="grey", bg="#121e2a", highlightthickness=0)
    Candidate6Btn = tkinter.Button(root, borderwidth=0, highlightthickness=0, activebackground="black")

    testLabel7 = Label(root, font=font1, fg="White", bg="#121e2a", highlightthickness=0)
    Candidate7Label = Label(root, font=font1, fg="White", bg="#121e2a", highlightthickness=0)
    Candidate7ClassLabel = Label(root, font=font1, fg="grey", bg="#121e2a", highlightthickness=0)
    Candidate7Btn = tkinter.Button(root, borderwidth=0, highlightthickness=0, activebackground="black")

    testLabel8 = Label(root, font=font1, fg="White", bg="#121e2a", highlightthickness=0)
    Candidate8Label = Label(root, font=font1, fg="White", bg="#121e2a", highlightthickness=0)
    Candidate8ClassLabel = Label(root, font=font1, fg="grey", bg="#121e2a", highlightthickness=0)
    Candidate8Btn = tkinter.Button(root, borderwidth=0, highlightthickness=0, activebackground="black")

    # Load first screen candidates (Head Boy at idx 0, Head Girl at idx 2)
    load_page_candidates(postlist[0], postlist[1], 0, 2, 2, 2)


def extclick(n):
    setup_first_screen()


root.bind_all('0', verify_unlock)
root.bind_all('<Control-Shift-Q>', exit_application)
root.bind_all('<Control-Shift-q>', exit_application)

setup_first_screen()
if windstat == True:
    root.mainloop()
else:
    pass

if 'cnx' in globals() and cnx is not None:
    try:
        cnx.close()
    except Exception:
        pass
