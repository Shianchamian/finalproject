"""
Database-related functions, including creating tables, saving face data,
listing all stored faces, and deleting or updating face records.
"""

import sqlite3
import numpy as np
import os
import time

DB_PATH = "database.db"

def init_db():
    """Create the database and tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS faces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            relation TEXT,
            image_path TEXT NOT NULL,
            features BLOB NOT NULL
        )
    """)

    # Create a table for recognition history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recognitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            relation TEXT NOT NULL,
            image_path TEXT NOT NULL,
            result TEXT NOT NULL,  -- "Success" or "Failed"
            timestamp INTEGER NOT NULL
        )
    """)

    conn.commit()
    conn.close()

def save_recognition(name, relation, image_path, result):
    """Store face recognition result into the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO recognitions (name, relation, image_path, result, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (name, relation, image_path, result, int(time.time())))
    conn.commit()
    conn.close()

def save_face_data(name, relation, image_path, features):
    """Save a new face record into the 'faces' table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO faces (name, relation, image_path, features)
        VALUES (?, ?, ?, ?)
    """, (name, relation, image_path, features.tobytes()))
    conn.commit()
    conn.close()

def manage_face():
    """
    Retrieve basic information (id, name, relation, image_path) for all faces
    from the database. This is used to populate the 'Manage Faces' screen.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, relation, image_path FROM faces")
    faces = cursor.fetchall()
    conn.close()
    return faces

def get_face():
    """Get (id, name, relation, features) for every face in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, relation, features FROM faces")
    faces = cursor.fetchall()
    conn.close()
    return faces

def delete_face(face_id):
    """Remove a face record by ID, also delete its associated image file if present."""
    face = get_face_by_id(face_id)
    if face and face['image_path']:
        try:
            if os.path.exists(face['image_path']):
                os.remove(face['image_path'])
        except Exception as e:
            print(f"Error deleting image file: {e}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM faces WHERE id=?", (face_id,))
    conn.commit()
    conn.close()

def update_face(face_id, new_name, new_relation):
    """Update name and relation fields for a specific face."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE faces SET name=?, relation=? WHERE id=?", (new_name, new_relation, face_id))
    conn.commit()
    conn.close()

def get_face_by_id(face_id):
    """Retrieve full face record (including image_path and features) by ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, relation, image_path, features FROM faces WHERE id=?", (face_id,))
    face = cursor.fetchone()
    conn.close()
    
    if face:
        return {
            'id': face[0],
            'name': face[1],
            'relation': face[2],
            'image_path': face[3],
            'features': face[4]
        }
    return None

def get_name_by_id(face_id):
    """Return just the 'name' field for a given face ID."""
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM faces WHERE id=?", (face_id,))
    name = cursor.fetchone()[0]
    conn.close()
    return name

def get_all_results():
    """Retrieve all recognition results, sorted by timestamp descending (newest first)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, relation, image_path, result, timestamp 
        FROM recognitions 
        ORDER BY timestamp DESC
    """)
    
    recognitions = cursor.fetchall()
    
    conn.close()
    return recognitions

def clear_recognition_history():
    """Delete all records from the recognitions table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM recognitions")
    conn.commit()
    conn.close()


def print_table_faces():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM faces")
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        print(row)

# print_table_faces()
