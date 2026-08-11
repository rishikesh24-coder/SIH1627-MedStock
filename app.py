from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import date, datetime


app = Flask(__name__)

DATABASE = "medstock.db"


def get_database_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


# ==================================================
# DASHBOARD
# ==================================================

@app.route("/")
def home():

    connection = get_database_connection()

    # -----------------------------------------------
    # COUNT HOSPITALS
    # -----------------------------------------------

    hospital_count = connection.execute(
        "SELECT COUNT(*) FROM hospitals"
    ).fetchone()[0]


    # -----------------------------------------------
    # COUNT MEDICINES
    # -----------------------------------------------

    medicine_count = connection.execute(
        "SELECT COUNT(*) FROM medicines"
    ).fetchone()[0]


    # -----------------------------------------------
    # LOW STOCK
    # -----------------------------------------------

    low_stock_items = connection.execute("""
        SELECT
            hospitals.name AS hospital_name,
            medicines.name AS medicine_name,
            inventory.stock_quantity,
            inventory.minimum_stock
        FROM inventory
        JOIN hospitals
            ON inventory.hospital_id = hospitals.id
        JOIN medicines
            ON inventory.medicine_id = medicines.id
        WHERE inventory.stock_quantity < inventory.minimum_stock
    """).fetchall()


    # -----------------------------------------------
    # EXPIRY INFORMATION
    # -----------------------------------------------

    inventory_items = connection.execute("""
        SELECT
            hospitals.name AS hospital_name,
            medicines.name AS medicine_name,
            inventory.expiry_date
        FROM inventory
        JOIN hospitals
            ON inventory.hospital_id = hospitals.id
        JOIN medicines
            ON inventory.medicine_id = medicines.id
    """).fetchall()


    # -----------------------------------------------
    # FIND NEAR EXPIRY MEDICINES
    # -----------------------------------------------

    near_expiry_items = []

    today = date.today()


    for item in inventory_items:

        expiry_date = datetime.strptime(
            item["expiry_date"],
            "%Y-%m-%d"
        ).date()

        days_remaining = (expiry_date - today).days


        if 0 <= days_remaining <= 30:

            near_expiry_items.append({
                "hospital_name": item["hospital_name"],
                "medicine_name": item["medicine_name"],
                "expiry_date": item["expiry_date"],
                "days_remaining": days_remaining
            })


    # -----------------------------------------------
    # TRANSFER RECOMMENDATIONS
    # -----------------------------------------------

    all_inventory = connection.execute("""
        SELECT
            inventory.hospital_id,
            inventory.medicine_id,
            hospitals.name AS hospital_name,
            medicines.name AS medicine_name,
            inventory.stock_quantity,
            inventory.minimum_stock
        FROM inventory
        JOIN hospitals
            ON inventory.hospital_id = hospitals.id
        JOIN medicines
            ON inventory.medicine_id = medicines.id
        ORDER BY inventory.medicine_id
    """).fetchall()


    transfer_recommendations = []


    # Group inventory by medicine
    medicine_groups = {}


    for item in all_inventory:

        medicine_id = item["medicine_id"]

        if medicine_id not in medicine_groups:

            medicine_groups[medicine_id] = []

        medicine_groups[medicine_id].append(item)


    # Find hospitals with excess and shortage
    for medicine_id, items in medicine_groups.items():

        donors = []
        recipients = []


        for item in items:

            excess = (
                item["stock_quantity"]
                - item["minimum_stock"]
            )

            shortage = (
                item["minimum_stock"]
                - item["stock_quantity"]
            )


            # Hospital has excess
            if excess > 0:

                donors.append({
                    "hospital_name": item["hospital_name"],
                    "medicine_name": item["medicine_name"],
                    "excess": excess
                })


            # Hospital has shortage
            elif shortage > 0:

                recipients.append({
                    "hospital_name": item["hospital_name"],
                    "medicine_name": item["medicine_name"],
                    "shortage": shortage
                })


        # Match donor with recipient
        for donor in donors:

            for recipient in recipients:

                transfer_quantity = min(
                    donor["excess"],
                    recipient["shortage"]
                )


                if transfer_quantity > 0:

                    transfer_recommendations.append({

                        "medicine_name":
                            donor["medicine_name"],

                        "from_hospital":
                            donor["hospital_name"],

                        "to_hospital":
                            recipient["hospital_name"],

                        "quantity":
                            transfer_quantity

                    })


    connection.close()


    # -----------------------------------------------
    # SEND DATA TO HTML
    # -----------------------------------------------

    return render_template(

        "index.html",

        hospital_count=hospital_count,

        medicine_count=medicine_count,

        low_stock_count=len(low_stock_items),

        low_stock_items=low_stock_items,

        near_expiry_items=near_expiry_items,

        transfer_recommendations=transfer_recommendations

    )


# ==================================================
# HOSPITALS
# ==================================================

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


# ==================================================
# ADD HOSPITAL
# ==================================================

@app.route("/add-hospital", methods=["POST"])
def add_hospital():

    name = request.form["name"]

    location = request.form["location"]


    connection = get_database_connection()


    connection.execute(
        """
        INSERT INTO hospitals
        (name, location)
        VALUES (?, ?)
        """,

        (name, location)
    )


    connection.commit()

    connection.close()


    return redirect("/hospitals")


# ==================================================
# MEDICINES
# ==================================================

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


# ==================================================
# ADD MEDICINE
# ==================================================

@app.route("/add-medicine", methods=["POST"])
def add_medicine():

    name = request.form["name"]

    category = request.form["category"]


    connection = get_database_connection()


    connection.execute(
        """
        INSERT INTO medicines
        (name, category)
        VALUES (?, ?)
        """,

        (name, category)
    )


    connection.commit()

    connection.close()


    return redirect("/medicines")


# ==================================================
# INVENTORY
# ==================================================

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


# ==================================================
# ADD INVENTORY
# ==================================================

@app.route("/add-inventory", methods=["POST"])
def add_inventory():

    hospital_id = request.form["hospital_id"]

    medicine_id = request.form["medicine_id"]

    stock_quantity = request.form["stock_quantity"]

    minimum_stock = request.form["minimum_stock"]

    expiry_date = request.form["expiry_date"]


    connection = get_database_connection()


    connection.execute(
        """
        INSERT INTO inventory
        (
            hospital_id,
            medicine_id,
            stock_quantity,
            minimum_stock,
            expiry_date
        )
        VALUES (?, ?, ?, ?, ?)
        """,

        (
            hospital_id,
            medicine_id,
            stock_quantity,
            minimum_stock,
            expiry_date
        )
    )


    connection.commit()

    connection.close()


    return redirect("/inventory")


# ==================================================
# START APPLICATION
# ==================================================

if __name__ == "__main__":

    app.run(debug=True)