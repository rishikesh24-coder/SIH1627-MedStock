from flask import Flask, render_template, request, redirect
import sqlite3


app = Flask(__name__)

DATABASE = "medstock.db"


def get_database_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


# =========================
# DASHBOARD
# =========================

@app.route("/")
def home():

    connection = get_database_connection()

    hospital_count = connection.execute(
        "SELECT COUNT(*) FROM hospitals"
    ).fetchone()[0]

    medicine_count = connection.execute(
        "SELECT COUNT(*) FROM medicines"
    ).fetchone()[0]

    low_stock_count = connection.execute("""
        SELECT COUNT(*)
        FROM inventory
        WHERE stock_quantity < minimum_stock
    """).fetchone()[0]

    connection.close()

    return render_template(
        "index.html",
        hospital_count=hospital_count,
        medicine_count=medicine_count,
        low_stock_count=low_stock_count
    )


# =========================
# HOSPITALS
# =========================

@app.route("/hospitals")
def hospitals():

    connection = get_database_connection()

    hospitals = connection.execute(
        "SELECT * FROM hospitals ORDER BY id"
    ).fetchall()

    connection.close()

    return render_template(
        "hospitals.html",
        hospitals=hospitals
    )


# =========================
# ADD HOSPITAL
# =========================

@app.route("/add-hospital", methods=["POST"])
def add_hospital():

    name = request.form["name"]
    location = request.form["location"]

    connection = get_database_connection()

    connection.execute(
        "INSERT INTO hospitals (name, location) VALUES (?, ?)",
        (name, location)
    )

    connection.commit()
    connection.close()

    return redirect("/hospitals")


# =========================
# MEDICINES
# =========================

@app.route("/medicines")
def medicines():

    connection = get_database_connection()

    medicines = connection.execute(
        "SELECT * FROM medicines ORDER BY id"
    ).fetchall()

    connection.close()

    return render_template(
        "medicines.html",
        medicines=medicines
    )


# =========================
# ADD MEDICINE
# =========================

@app.route("/add-medicine", methods=["POST"])
def add_medicine():

    name = request.form["name"]
    category = request.form["category"]

    connection = get_database_connection()

    connection.execute(
        "INSERT INTO medicines (name, category) VALUES (?, ?)",
        (name, category)
    )

    connection.commit()
    connection.close()

    return redirect("/medicines")


# =========================
# INVENTORY
# =========================

@app.route("/inventory")
def inventory():

    connection = get_database_connection()

    inventory_items = connection.execute("""
        SELECT
            inventory.id,
            hospitals.name AS hospital_name,
            medicines.name AS medicine_name,
            inventory.stock_quantity,
            inventory.minimum_stock,
            inventory.expiry_date
        FROM inventory
        JOIN hospitals
            ON inventory.hospital_id = hospitals.id
        JOIN medicines
            ON inventory.medicine_id = medicines.id
        ORDER BY inventory.id
    """).fetchall()

    hospitals = connection.execute(
        "SELECT * FROM hospitals ORDER BY name"
    ).fetchall()

    medicines = connection.execute(
        "SELECT * FROM medicines ORDER BY name"
    ).fetchall()

    connection.close()

    return render_template(
        "inventory.html",
        inventory_items=inventory_items,
        hospitals=hospitals,
        medicines=medicines
    )


# =========================
# ADD INVENTORY
# =========================

@app.route("/add-inventory", methods=["POST"])
def add_inventory():

    hospital_id = request.form["hospital_id"]
    medicine_id = request.form["medicine_id"]
    stock_quantity = request.form["stock_quantity"]
    minimum_stock = request.form["minimum_stock"]
    expiry_date = request.form["expiry_date"]

    connection = get_database_connection()

    connection.execute("""
        INSERT INTO inventory
        (
            hospital_id,
            medicine_id,
            stock_quantity,
            minimum_stock,
            expiry_date
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        hospital_id,
        medicine_id,
        stock_quantity,
        minimum_stock,
        expiry_date
    ))

    connection.commit()
    connection.close()

    return redirect("/inventory")


if __name__ == "__main__":
    app.run(debug=True)