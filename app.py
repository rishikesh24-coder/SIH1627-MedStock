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


if __name__ == "__main__":
    app.run(debug=True)