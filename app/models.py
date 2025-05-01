# app/models.py
import sqlite3
import hashlib

DB_PATH = "db_web.db"

class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    @staticmethod
    def create_table():
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        con.commit()
        con.close()

    def save(self):
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        hashed_pw = hashlib.sha256(self.password.encode()).hexdigest()
        try:
            cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (self.username, hashed_pw))
            con.commit()
        except sqlite3.IntegrityError:
            con.close()
            return False
        con.close()
        return True

    @staticmethod
    def authenticate(username, password):
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        cur.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_pw))
        user = cur.fetchone()
        con.close()
        return user is not None
