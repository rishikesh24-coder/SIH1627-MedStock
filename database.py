import sqlite3
from datetime import date, timedelta

DATABASE = "medstock.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hospitals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location TEXT NOT NULL,
            contact TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            batch_number TEXT NOT NULL,
            expiry_date TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hospital_id INTEGER NOT NULL,
            medicine_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 0,
            min_stock INTEGER NOT NULL DEFAULT 20,
            FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE,
            FOREIGN KEY (medicine_id) REFERENCES medicines(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS requirements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hospital_id INTEGER NOT NULL,
            medicine_id INTEGER NOT NULL,
            required_quantity INTEGER NOT NULL,
            FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE,
            FOREIGN KEY (medicine_id) REFERENCES medicines(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transfers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_hospital_id INTEGER NOT NULL,
            to_hospital_id INTEGER NOT NULL,
            medicine_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'Suggested',
            transfer_date TEXT NOT NULL,
            FOREIGN KEY (from_hospital_id) REFERENCES hospitals(id),
            FOREIGN KEY (to_hospital_id) REFERENCES hospitals(id),
            FOREIGN KEY (medicine_id) REFERENCES medicines(id)
        )
    """)

    conn.commit()

    # Add demonstration data only when database is empty
    hospital_count = cursor.execute(
        "SELECT COUNT(*) FROM hospitals"
    ).fetchone()[0]

    if hospital_count == 0:
        hospitals = [
            ("District Hospital Kalyan", "Kalyan", "9876543210"),
            ("Government Hospital Thane", "Thane", "9876543211"),
            ("Civil Hospital Mumbai", "Mumbai", "9876543212"),
            ("Rural Hospital Dombivli", "Dombivli", "9876543213")
        ]

        cursor.executemany("""
            INSERT INTO hospitals (name, location, contact)
            VALUES (?, ?, ?)
        """, hospitals)

        today = date.today()

        medicines = [
            ("Paracetamol 500mg", "Tablet", "PCM001",
             (today + timedelta(days=180)).isoformat()),

            ("Amoxicillin 500mg", "Capsule", "AMX002",
             (today + timedelta(days=40)).isoformat()),

            ("Azithromycin 500mg", "Tablet", "AZI003",
             (today + timedelta(days=250)).isoformat()),

            ("Metformin 500mg", "Tablet", "MET004",
             (today + timedelta(days=75)).isoformat()),

            ("ORS Sachet", "Powder", "ORS005",
             (today + timedelta(days=300)).isoformat())
        ]

        cursor.executemany("""
            INSERT INTO medicines
            (name, category, batch_number, expiry_date)
            VALUES (?, ?, ?, ?)
        """, medicines)

        # Inventory
        inventory = [
            (1, 1, 20, 50),
            (2, 1, 500, 100),
            (3, 1, 150, 50),
            (4, 1, 30, 40),

            (1, 2, 25, 50),
            (2, 2, 300, 100),
            (3, 2, 80, 40),
            (4, 2, 10, 30),

            (1, 3, 100, 50),
            (2, 3, 50, 40),
            (3, 3, 300, 100),
            (4, 3, 25, 40),

            (1, 4, 20, 50),
            (2, 4, 250, 100),
            (3, 4, 100, 50),
            (4, 4, 15, 30),

            (1, 5, 200, 100),
            (2, 5, 500, 100),
            (3, 5, 100, 50),
            (4, 5, 40, 50)
        ]

        cursor.executemany("""
            INSERT INTO inventory
            (hospital_id, medicine_id, quantity, min_stock)
            VALUES (?, ?, ?, ?)
        """, inventory)

        # Requirements
        requirements = [
            (1, 1, 200),
            (4, 1, 150),
            (1, 2, 100),
            (4, 2, 80),
            (1, 4, 120),
            (4, 4, 100),
            (2, 5, 300)
        ]

        cursor.executemany("""
            INSERT INTO requirements
            (hospital_id, medicine_id, required_quantity)
            VALUES (?, ?, ?)
        """, requirements)

        conn.commit()

    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")