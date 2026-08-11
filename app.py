from flask import Flask, render_template, request, redirect, url_for, flash
from database import get_db_connection, init_db
from datetime import date, timedelta

app = Flask(__name__)
app.secret_key = "medstock-secret-key"

init_db()


@app.route("/")
def dashboard():
    conn = get_db_connection()

    hospitals = conn.execute(
        "SELECT COUNT(*) AS count FROM hospitals"
    ).fetchone()["count"]

    medicines = conn.execute(
        "SELECT COUNT(*) AS count FROM medicines"
    ).fetchone()["count"]

    low_stock = conn.execute("""
        SELECT COUNT(*) AS count
        FROM inventory
        WHERE quantity <= min_stock
    """).fetchone()["count"]

    today = date.today()
    expiry_limit = today + timedelta(days=90)

    near_expiry = conn.execute("""
        SELECT COUNT(*) AS count
        FROM medicines
        WHERE date(expiry_date) <= date(?)
    """, (expiry_limit.isoformat(),)).fetchone()["count"]

    requirements = conn.execute("""
        SELECT COUNT(*) AS count
        FROM requirements
    """).fetchone()["count"]

    suggested_transfers = get_transfer_suggestions(conn)

    recent_transfers = conn.execute("""
        SELECT
            t.id,
            h1.name AS from_hospital,
            h2.name AS to_hospital,
            m.name AS medicine_name,
            t.quantity,
            t.status,
            t.transfer_date
        FROM transfers t
        JOIN hospitals h1 ON t.from_hospital_id = h1.id
        JOIN hospitals h2 ON t.to_hospital_id = h2.id
        JOIN medicines m ON t.medicine_id = m.id
        ORDER BY t.id DESC
        LIMIT 5
    """).fetchall()

    conn.close()

    return render_template(
        "index.html",
        hospitals=hospitals,
        medicines=medicines,
        low_stock=low_stock,
        near_expiry=near_expiry,
        requirements=requirements,
        suggestions=suggested_transfers,
        recent_transfers=recent_transfers
    )


@app.route("/hospitals")
def hospitals_page():
    conn = get_db_connection()

    hospitals = conn.execute("""
        SELECT * FROM hospitals
        ORDER BY name
    """).fetchall()

    conn.close()

    return render_template("hospitals.html", hospitals=hospitals)


@app.route("/hospitals/add", methods=["POST"])
def add_hospital():
    name = request.form["name"]
    location = request.form["location"]
    contact = request.form["contact"]

    conn = get_db_connection()

    conn.execute("""
        INSERT INTO hospitals (name, location, contact)
        VALUES (?, ?, ?)
    """, (name, location, contact))

    conn.commit()
    conn.close()

    flash("Hospital added successfully.", "success")

    return redirect(url_for("hospitals_page"))


@app.route("/medicines")
def medicines_page():
    conn = get_db_connection()

    medicines = conn.execute("""
        SELECT * FROM medicines
        ORDER BY expiry_date
    """).fetchall()

    conn.close()

    return render_template("medicines.html", medicines=medicines)


@app.route("/medicines/add", methods=["POST"])
def add_medicine():
    name = request.form["name"]
    category = request.form["category"]
    batch_number = request.form["batch_number"]
    expiry_date = request.form["expiry_date"]

    conn = get_db_connection()

    conn.execute("""
        INSERT INTO medicines
        (name, category, batch_number, expiry_date)
        VALUES (?, ?, ?, ?)
    """, (name, category, batch_number, expiry_date))

    conn.commit()
    conn.close()

    flash("Medicine added successfully.", "success")

    return redirect(url_for("medicines_page"))


@app.route("/inventory")
def inventory_page():
    conn = get_db_connection()

    inventory = conn.execute("""
        SELECT
            inventory.id,
            hospitals.name AS hospital_name,
            medicines.name AS medicine_name,
            medicines.batch_number,
            medicines.expiry_date,
            inventory.quantity,
            inventory.min_stock
        FROM inventory
        JOIN hospitals ON inventory.hospital_id = hospitals.id
        JOIN medicines ON inventory.medicine_id = medicines.id
        ORDER BY hospitals.name, medicines.name
    """).fetchall()

    hospitals = conn.execute(
        "SELECT * FROM hospitals ORDER BY name"
    ).fetchall()

    medicines = conn.execute(
        "SELECT * FROM medicines ORDER BY name"
    ).fetchall()

    conn.close()

    return render_template(
        "inventory.html",
        inventory=inventory,
        hospitals=hospitals,
        medicines=medicines
    )


@app.route("/inventory/add", methods=["POST"])
def add_inventory():
    hospital_id = request.form["hospital_id"]
    medicine_id = request.form["medicine_id"]
    quantity = int(request.form["quantity"])
    min_stock = int(request.form["min_stock"])

    conn = get_db_connection()

    existing = conn.execute("""
        SELECT id
        FROM inventory
        WHERE hospital_id = ? AND medicine_id = ?
    """, (hospital_id, medicine_id)).fetchone()

    if existing:
        conn.execute("""
            UPDATE inventory
            SET quantity = quantity + ?, min_stock = ?
            WHERE id = ?
        """, (quantity, min_stock, existing["id"]))

        message = "Inventory updated successfully."
    else:
        conn.execute("""
            INSERT INTO inventory
            (hospital_id, medicine_id, quantity, min_stock)
            VALUES (?, ?, ?, ?)
        """, (hospital_id, medicine_id, quantity, min_stock))

        message = "Inventory added successfully."

    conn.commit()
    conn.close()

    flash(message, "success")

    return redirect(url_for("inventory_page"))


@app.route("/requirements")
def requirements_page():
    conn = get_db_connection()

    requirements = conn.execute("""
        SELECT
            r.id,
            hospitals.name AS hospital_name,
            medicines.name AS medicine_name,
            r.required_quantity,
            COALESCE(i.quantity, 0) AS current_stock,
            CASE
                WHEN r.required_quantity - COALESCE(i.quantity, 0) > 0
                THEN r.required_quantity - COALESCE(i.quantity, 0)
                ELSE 0
            END AS shortage
        FROM requirements r
        JOIN hospitals ON r.hospital_id = hospitals.id
        JOIN medicines ON r.medicine_id = medicines.id
        LEFT JOIN inventory i
            ON i.hospital_id = r.hospital_id
            AND i.medicine_id = r.medicine_id
        ORDER BY shortage DESC
    """).fetchall()

    hospitals = conn.execute(
        "SELECT * FROM hospitals ORDER BY name"
    ).fetchall()

    medicines = conn.execute(
        "SELECT * FROM medicines ORDER BY name"
    ).fetchall()

    conn.close()

    return render_template(
        "requirements.html",
        requirements=requirements,
        hospitals=hospitals,
        medicines=medicines
    )


@app.route("/requirements/add", methods=["POST"])
def add_requirement():
    hospital_id = request.form["hospital_id"]
    medicine_id = request.form["medicine_id"]
    required_quantity = int(request.form["required_quantity"])

    conn = get_db_connection()

    conn.execute("""
        INSERT INTO requirements
        (hospital_id, medicine_id, required_quantity)
        VALUES (?, ?, ?)
    """, (hospital_id, medicine_id, required_quantity))

    conn.commit()
    conn.close()

    flash("Requirement added successfully.", "success")

    return redirect(url_for("requirements_page"))


@app.route("/transfers")
def transfers_page():
    conn = get_db_connection()

    suggestions = get_transfer_suggestions(conn)

    transfers = conn.execute("""
        SELECT
            t.id,
            h1.name AS from_hospital,
            h2.name AS to_hospital,
            m.name AS medicine_name,
            t.quantity,
            t.status,
            t.transfer_date
        FROM transfers t
        JOIN hospitals h1 ON t.from_hospital_id = h1.id
        JOIN hospitals h2 ON t.to_hospital_id = h2.id
        JOIN medicines m ON t.medicine_id = m.id
        ORDER BY t.id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "transfers.html",
        suggestions=suggestions,
        transfers=transfers
    )


@app.route("/transfers/create", methods=["POST"])
def create_transfer():
    from_hospital_id = request.form["from_hospital_id"]
    to_hospital_id = request.form["to_hospital_id"]
    medicine_id = request.form["medicine_id"]
    quantity = int(request.form["quantity"])

    if from_hospital_id == to_hospital_id:
        flash("Source and destination hospitals cannot be the same.", "error")
        return redirect(url_for("transfers_page"))

    conn = get_db_connection()

    source = conn.execute("""
        SELECT quantity
        FROM inventory
        WHERE hospital_id = ? AND medicine_id = ?
    """, (from_hospital_id, medicine_id)).fetchone()

    if not source or source["quantity"] < quantity:
        flash("Transfer quantity is greater than available stock.", "error")
        conn.close()
        return redirect(url_for("transfers_page"))

    conn.execute("""
        INSERT INTO transfers
        (from_hospital_id, to_hospital_id, medicine_id,
         quantity, status, transfer_date)
        VALUES (?, ?, ?, ?, 'Completed', ?)
    """, (
        from_hospital_id,
        to_hospital_id,
        medicine_id,
        quantity,
        date.today().isoformat()
    ))

    conn.execute("""
        UPDATE inventory
        SET quantity = quantity - ?
        WHERE hospital_id = ? AND medicine_id = ?
    """, (quantity, from_hospital_id, medicine_id))

    destination = conn.execute("""
        SELECT id
        FROM inventory
        WHERE hospital_id = ? AND medicine_id = ?
    """, (to_hospital_id, medicine_id)).fetchone()

    if destination:
        conn.execute("""
            UPDATE inventory
            SET quantity = quantity + ?
            WHERE hospital_id = ? AND medicine_id = ?
        """, (quantity, to_hospital_id, medicine_id))
    else:
        conn.execute("""
            INSERT INTO inventory
            (hospital_id, medicine_id, quantity, min_stock)
            VALUES (?, ?, ?, 20)
        """, (to_hospital_id, medicine_id, quantity))

    conn.commit()
    conn.close()

    flash("Medicine transfer completed successfully.", "success")

    return redirect(url_for("transfers_page"))


def get_transfer_suggestions(conn):
    inventory_rows = conn.execute("""
        SELECT
            i.hospital_id,
            i.medicine_id,
            i.quantity,
            i.min_stock,
            h.name AS hospital_name,
            m.name AS medicine_name
        FROM inventory i
        JOIN hospitals h ON i.hospital_id = h.id
        JOIN medicines m ON i.medicine_id = m.id
    """).fetchall()

    suggestions = []

    for item in inventory_rows:

        # Hospital has shortage
        requirement = conn.execute("""
            SELECT required_quantity
            FROM requirements
            WHERE hospital_id = ? AND medicine_id = ?
            ORDER BY id DESC
            LIMIT 1
        """, (item["hospital_id"], item["medicine_id"])).fetchone()

        if not requirement:
            continue

        shortage = requirement["required_quantity"] - item["quantity"]

        if shortage <= 0:
            continue

        # Find hospitals having excess stock of same medicine
        donors = conn.execute("""
            SELECT
                i.hospital_id,
                i.quantity,
                i.min_stock,
                h.name AS hospital_name
            FROM inventory i
            JOIN hospitals h ON i.hospital_id = h.id
            WHERE i.medicine_id = ?
              AND i.hospital_id != ?
              AND i.quantity > i.min_stock
            ORDER BY (i.quantity - i.min_stock) DESC
        """, (item["medicine_id"], item["hospital_id"])).fetchall()

        remaining_shortage = shortage

        for donor in donors:

            excess = donor["quantity"] - donor["min_stock"]

            if excess <= 0:
                continue

            transfer_quantity = min(excess, remaining_shortage)

            suggestions.append({
                "from_hospital_id": donor["hospital_id"],
                "from_hospital": donor["hospital_name"],
                "to_hospital_id": item["hospital_id"],
                "to_hospital": item["hospital_name"],
                "medicine_id": item["medicine_id"],
                "medicine_name": item["medicine_name"],
                "quantity": transfer_quantity,
                "shortage": shortage
            })

            remaining_shortage -= transfer_quantity

            if remaining_shortage <= 0:
                break

    return suggestions


@app.route("/seed")
def seed_page():
    init_db()
    flash("Demo database initialized.", "success")
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(debug=True)