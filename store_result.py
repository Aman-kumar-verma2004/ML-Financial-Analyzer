import os
import json
import numpy as np
import mysql.connector
import joblib
from dotenv import load_dotenv

load_dotenv()

# Load model
model = joblib.load("model.joblib")

# MySQL DB setup
db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    database=os.getenv("DB_NAME")
)
cursor = db.cursor()

DATA_DIR = "data"

def extract_features(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)

    company = data.get("company", {})
    analysis = data.get("analysis", {})
    profit = data.get("data", {}).get("profitandloss", [])
    balance = data.get("data", {}).get("balancesheet", [])

    try:
        roe = float(company.get("roe_percentage") or 0)
        sales_growth = float(analysis.get("sales_growth") or 0)
        dividend = float(analysis.get("dividend_payout") or 0)

        latest = profit[-1] if profit else {}
        net_profit = float(latest.get("net_profit") or 1)
        sales = float(latest.get("sales") or 1)
        profit_margin = (net_profit / sales) * 100

        latest_bal = balance[-1] if balance else {}
        borrowings = float(latest_bal.get("borrowings") or 0)
        reserves = float(latest_bal.get("reserves") or 1)
        debt_to_equity = borrowings / reserves

        return {
            "roe": roe,
            "sales_growth": sales_growth,
            "dividend": dividend,
            "profit_margin": profit_margin,
            "debt_to_equity": debt_to_equity
        }
    except:
        return None

def pick_pros_cons(analysis):
    pros = []
    cons = []

    if not isinstance(analysis, list):
        return pros, cons

    for point in analysis:
        if any(val in point.lower() for val in ["debt-free", "growth", "dividend", "healthy", "good", "roe", "profit"]):
            pros.append(point)
        elif any(val in point.lower() for val in ["poor", "low", "not", "decline"]):
            cons.append(point)

    return pros[:3], cons[:3]  # only top 3

def store_to_db(company_id, pros, cons, label):
    try:
        cursor.execute(
            "INSERT INTO ml (company, pros, cons, strngth) VALUES (%s, %s, %s, %s)",
            (company_id, "\n".join(pros), "\n".join(cons), label)
        )
        db.commit()
        print(f"✅ Inserted → {company_id} ({label})")
    except Exception as e:
        print(f"❌ DB insert failed for {company_id}: {e}")

def main():
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".json"):
            company_id = filename.replace(".json", "")
            path = os.path.join(DATA_DIR, filename)

            try:
                with open(path, 'r') as f:
                    data = json.load(f)

                features = extract_features(path)
                if features is None:
                    print(f"⚠️ Skipped {company_id}: invalid data")
                    continue

                row = np.array([list(features.values())])
                label = model.predict(row)[0]

                analysis = data.get("analysis", {}).get("points", [])
                pros, cons = pick_pros_cons(analysis)

                store_to_db(company_id, pros, cons, label)

            except Exception as e:
                print(f"❌ Failed for {company_id}: {e}")

    print("🎉 All data inserted into MySQL.")

if __name__ == "__main__":
    main()
