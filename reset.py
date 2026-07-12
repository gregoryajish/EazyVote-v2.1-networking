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

import sqlite3

mysql_reset_success = False
try:
    db_config = load_db_config()
    cnx=mysql.connector.connect(user=db_config["db_user"], password=db_config["db_password"], host=db_config["db_host"], database=db_config["db_name"])
    cursor = cnx.cursor()
    cursor.execute('update votes set votes=0')
    cnx.commit()
    cnx.close()
    print("MySQL Database reset completed successfully!")
    mysql_reset_success = True
except Exception as e:
    print(f"Warning: Failed to reset MySQL database (might be offline): {e}")

# Reset local SQLite database
sqlite_path = get_path("local_voting.db")
try:
    lite_con = sqlite3.connect(sqlite_path)
    lite_cur = lite_con.cursor()
    lite_cur.execute('UPDATE votes SET votes=0')
    lite_cur.execute('DELETE FROM offline_votes')
    lite_con.commit()
    lite_con.close()
    print("Local SQLite database reset completed successfully (votes reset, offline votes cleared)!")
except Exception as e:
    print(f"Error resetting local SQLite database: {e}")
    if not mysql_reset_success:
        sys.exit(1)

