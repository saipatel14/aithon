from flask import Flask, request, jsonify, send_file
import sqlite3
import pandas as pd

app = Flask(__name__)
DB = 'data.db'


# ----------------------- DB SETUP -----------------------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # Create Transactions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            amount REAL,
            description TEXT,
            category TEXT
        )
    ''')

    # Create Budgets table
    c.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            amount REAL
        )
    ''')

    # Create Goals table
    c.execute('''
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            target REAL
        )
    ''')

    conn.commit()
    conn.close()


# ------------------ CATEGORIZATION ---------------------
def auto_categorize(description):
    desc = description.lower()
    if "uber" in desc or "ola" in desc:
        return "Transport"
    elif "coffee" in desc or "starbucks" in desc:
        return "Food & Drinks"
    elif "rent" in desc:
        return "Housing"
    elif "electricity" in desc or "bill" in desc:
        return "Utilities"
    else:
        return "Misc"


# ------------------ API ENDPOINTS ----------------------

@app.route('/transactions', methods=['POST'])
def add_transaction():
    data = request.json
    date = data.get("date")
    amount = data.get("amount")
    description = data.get("description")
    category = data.get("category") or auto_categorize(description)

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO transactions (date, amount, description, category) VALUES (?, ?, ?, ?)",
              (date, amount, description, category))
    conn.commit()
    conn.close()
    return jsonify({"message": "Transaction added"}), 201


@app.route('/transactions', methods=['GET'])
def get_transactions():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM transactions")
    rows = c.fetchall()
    conn.close()

    result = [{
        "id": row[0],
        "date": row[1],
        "amount": row[2],
        "description": row[3],
        "category": row[4]
    } for row in rows]

    return jsonify(result)


@app.route('/budgets', methods=['POST'])
def add_budget():
    data = request.json
    category = data.get("category")
    amount = data.get("amount")

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO budgets (category, amount) VALUES (?, ?)", (category, amount))
    conn.commit()
    conn.close()
    return jsonify({"message": "Budget added"})


@app.route('/goals', methods=['POST'])
def add_goal():
    data = request.json
    name = data.get("name")
    target = data.get("target")

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO goals (name, target) VALUES (?, ?)", (name, target))
    conn.commit()
    conn.close()
    return jsonify({"message": "Goal added"})


@app.route('/reset', methods=['POST'])
def reset_all_data():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM transactions")
    c.execute("DELETE FROM budgets")
    c.execute("DELETE FROM goals")
    conn.commit()
    conn.close()
    return jsonify({"message": "All data reset"})


@app.route('/export', methods=['GET'])
def export_transactions():
    conn = sqlite3.connect(DB)
    df = pd.read_sql_query("SELECT * FROM transactions", conn)
    conn.close()
    export_file = "transactions.csv"
    df.to_csv(export_file, index=False)
    return send_file(export_file, as_attachment=True)


# ------------------ MAIN ----------------------
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
