import sqlite3


DATABASE = "medstock.db"


def create_database():
    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    # Hospitals table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hospitals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location TEXT NOT NULL
        )
    """)

    # Medicines table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL
        )
    """)

    # Inventory table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hospital_id INTEGER NOT NULL,
            medicine_id INTEGER NOT NULL,
            stock_quantity INTEGER NOT NULL,
            minimum_stock INTEGER NOT NULL,
            expiry_date TEXT NOT NULL,
            FOREIGN KEY (hospital_id) REFERENCES hospitals(id),
            FOREIGN KEY (medicine_id) REFERENCES medicines(id)
        )
    """)

    connection.commit()
    connection.close()

    print("Database created successfully!")


if __name__ == "__main__":
    create_database()
    import sqlite3


DATABASE = "medstock.db"


def create_database():

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    # -------------------------
    # HOSPITALS TABLE
    # -------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hospitals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location TEXT NOT NULL
        )
    """)

    # -------------------------
    # MEDICINES TABLE
    # -------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL
        )
    """)

    # -------------------------
    # INVENTORY TABLE
    # -------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hospital_id INTEGER NOT NULL,
            medicine_id INTEGER NOT NULL,
            stock_quantity INTEGER NOT NULL,
            minimum_stock INTEGER NOT NULL,
            expiry_date TEXT NOT NULL,
            FOREIGN KEY (hospital_id) REFERENCES hospitals(id),
            FOREIGN KEY (medicine_id) REFERENCES medicines(id)
        )
    """)

    # -------------------------
    # SAMPLE HOSPITALS
    # -------------------------

    cursor.execute("""
        INSERT OR IGNORE INTO hospitals (id, name, location)
        VALUES (1, 'Kalyan Government Hospital', 'Kalyan')
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO hospitals (id, name, location)
        VALUES (2, 'Thane Government Hospital', 'Thane')
    """)

    # -------------------------
    # SAMPLE MEDICINES
    # -------------------------

    cursor.execute("""
        INSERT OR IGNORE INTO medicines (id, name, category)
        VALUES (1, 'Paracetamol', 'Tablet')
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO medicines (id, name, category)
        VALUES (2, 'Amoxicillin', 'Antibiotic')
    """)

    # -------------------------
    # SAMPLE INVENTORY
    # -------------------------

    cursor.execute("""
        INSERT OR IGNORE INTO inventory
        (id, hospital_id, medicine_id, stock_quantity, minimum_stock, expiry_date)
        VALUES (1, 1, 1, 500, 100, '2027-01-20')
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO inventory
        (id, hospital_id, medicine_id, stock_quantity, minimum_stock, expiry_date)
        VALUES (2, 2, 1, 30, 100, '2026-12-10')
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO inventory
        (id, hospital_id, medicine_id, stock_quantity, minimum_stock, expiry_date)
        VALUES (3, 1, 2, 50, 100, '2026-08-25')
    """)

    connection.commit()

    connection.close()

    print("Database created successfully!")
    print("Sample data added successfully!")


if __name__ == "__main__":
    create_database()