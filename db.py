import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "chatbot.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tickets (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      order_no TEXT,
      issue_type TEXT,
      description TEXT,
      status TEXT,
      created_at TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS chats (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      session_id TEXT,
      sender TEXT,
      message TEXT,
      created_at TEXT
    )
    """)
    conn.commit()
    conn.close()

def create_ticket(order_no, issue_type, description):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    created_at = datetime.utcnow().isoformat()
    cur.execute("INSERT INTO tickets (order_no, issue_type, description, status, created_at) VALUES (?, ?, ?, ?, ?)",
                (order_no, issue_type, description, "open", created_at))
    ticket_id = cur.lastrowid
    conn.commit()
    conn.close()
    return ticket_id

def save_chat(session_id, sender, message):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    created_at = datetime.utcnow().isoformat()
    cur.execute("INSERT INTO chats (session_id, sender, message, created_at) VALUES (?, ?, ?, ?)",
                (session_id, sender, message, created_at))
    conn.commit()
    conn.close()
