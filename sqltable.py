import mysql.connector
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

# Connect to MySQL Server
try:
    db_config = load_db_config()
    con = mysql.connector.connect(host=db_config["db_host"], user=db_config["db_user"], password=db_config["db_password"])
    cur = con.cursor()
except Exception as e:
    print(f"Failed to connect to MySQL Server: {e}")
    sys.exit(1)

# Create and select database
cur.execute(f"create database if not exists {db_config['db_name']}")
cur.execute(f"use {db_config['db_name']}")

# Recreate candidate table
cur.execute("drop table if exists candidate")
cur.execute("Create table candidate(Serial_No int, Name varchar(30), class varchar(6), Post varchar(20))")
cur.execute("alter table candidate add unique index(Serial_No)")

# Recreate votes table
cur.execute("drop table if exists votes")
cur.execute("Create table votes(Serial_No int, Name varchar(30), votes int)")
cur.execute("alter table votes add unique index(Serial_No)")

# List of new candidates (Serial_No, Name, Class, Post)
candidates = [
    # Head Boy (2 candidates)
    (1, "Lious Basil Joshy", "XII A", "Head Boy"),
    (2, "Daniel Saji", "XI A", "Head Boy"),
    
    # Head Girl (2 candidates)
    (3, "Meera P V", "XII C", "Head Girl"),
    (4, "Aida Jojo", "XI B", "Head Girl"),
    
    # Sports Boy (2 candidates)
    (5, "Noha Binil", "XII A", "Sports Boy"),
    (6, "Abhinav Krishna P", "XI A", "Sports Boy"),
    
    # Sports Girl (2 candidates)
    (7, "Abhinaya Suresh", "XII B", "Sports Girl"),
    (8, "Delna Mariya Jaison", "XI B", "Sports Girl"),
    
    # Arts Boy (2 candidates)
    (9, "Naveen T.S", "XII A", "Arts Boy"),
    (10, "Chris Ullas", "XI B", "Arts Boy"),
    
    # Arts Girl (2 candidates)
    (11, "Krishnanandha P.S", "XII B", "Arts Girl"),
    (12, "Aagna Maria Sabu", "XI B", "Arts Girl"),
    
    # Discipline Boy (2 candidates)
    (13, "Adith Anuraj", "XII A", "Discipline Boy"),
    (14, "Geevarghese Basil", "XI A", "Discipline Boy"),
    
    # Discipline Girl (2 candidates)
    (15, "Annmaria Ashly", "XII B", "Discipline Girl"),
    (16, "Dilsha Nasrin", "XI B", "Discipline Girl")
]

import sqlite3

# Insert candidates and initialize votes
for c in candidates:
    cur.execute("insert into candidate values(%s, %s, %s, %s)", c)
    cur.execute("insert into votes values(%s, %s, 0)", (c[0], c[1]))

con.commit()
con.close()
print("MySQL Database initialized successfully with 16 candidates!")

# Initialize local SQLite database
sqlite_path = get_path("local_voting.db")
try:
    if os.path.exists(sqlite_path):
        os.remove(sqlite_path)
except Exception as e:
    print(f"Warning: Could not remove old local database file: {e}")

try:
    lite_con = sqlite3.connect(sqlite_path)
    lite_cur = lite_con.cursor()
    
    lite_cur.execute("CREATE TABLE IF NOT EXISTS candidate (Serial_No INTEGER PRIMARY KEY, Name TEXT, class TEXT, Post TEXT)")
    lite_cur.execute("CREATE TABLE IF NOT EXISTS votes (Serial_No INTEGER PRIMARY KEY, Name TEXT, votes INTEGER)")
    lite_cur.execute("CREATE TABLE IF NOT EXISTS offline_votes (id INTEGER PRIMARY KEY AUTOINCREMENT, Serial_No INTEGER, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
    
    for c in candidates:
        lite_cur.execute("INSERT OR REPLACE INTO candidate (Serial_No, Name, class, Post) VALUES (?, ?, ?, ?)", c)
        lite_cur.execute("INSERT OR REPLACE INTO votes (Serial_No, Name, votes) VALUES (?, ?, 0)", (c[0], c[1]))
        
    lite_con.commit()
    lite_con.close()
    print("Local SQLite database initialized successfully with 16 candidates!")
except Exception as e:
    print(f"Error: Failed to initialize local SQLite database: {e}")

