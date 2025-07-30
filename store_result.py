import os
import json
import numpy as np
import mysql.connector
import joblib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Configuration ---
MODEL_PATH = "model.joblib"
DATA_DIR = "data"
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

# --- Helper Functions ---
def safe_float(value, default=0.0):
    """Safely convert to float, returning a default on failure."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def extract_features(file_path):
    """Extracts features from a JSON file, ensuring data integrity."""
    with open(file_path, 'r') as f:
        data = json.load(f)

    company = data.get("company", {})
    analysis = data.get("analysis", {})
    profit = data.get("data", {}).get("profitandloss", [])
    balance = data.get("data", {}).get("balancesheet", [])

    roe = safe_float(company.get("roe_percentage"))
    sales_growth = safe_float(analysis.get("sales_growth"))
    dividend = safe_float(analysis.get("dividend_payout"))

    profit_margin = 0.0
    if profit:
        latest_profit = profit[-1]
        net_profit = safe_float(latest_profit.get("net_profit"))
        sales = safe_float(latest_profit.get("sales"))
        if sales > 0:
            profit_margin = (net_profit / sales) * 100

    debt_to_equity = 0.0
    if balance:
        latest_balance = balance[-1]
        borrowings = safe_float(latest_balance.get("borrowings"))
        reserves = safe_float(latest_balance.get("reserves"))
        if reserves > 0:
            debt_to_equity = borrowings / reserves

    return {
        "roe": roe,
        "sales_growth": sales_growth,
        "dividend": dividend,
        "profit_margin": profit_margin,
        "debt_to_equity": debt_to_equity,
    }

def pick_pros_cons(analysis_points):
    """Categorizes analysis points into pros and cons."""
    pros, cons = [], []
    if not isinstance(analysis_points, list):
        return pros, cons

    pro_keywords = ["debt-free", "growth", "dividend", "healthy", "good", "roe", "profit"]
    con_keywords = ["poor", "low", "not", "decline", "pressure"]

    for point in analysis_points:
        point_lower = point.lower()
        if any(kw in point_lower for kw in pro_keywords):
            pros.append(point)
        elif any(kw in point_lower for kw in con_keywords):
            cons.append(point)
            
    return pros[:3], cons[:3]  # Return top 3 of each

def store_to_db(cursor, company_id, pros, cons, label):
    """Insert or update a company's analysis in the database."""
    sql = """
    INSERT INTO ml (company, pros, cons, strngth) 
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE 
        pros = VALUES(pros),
        cons = VALUES(cons),
        strngth = VALUES(strngth)
    """
    try:
        cursor.execute(sql, (company_id, "\n".join(pros), "\n".join(cons), label))
        print(f"✅ Upserted → {company_id} ({label})")
    except mysql.connector.Error as err:
        print(f"❌ DB insert/update failed for {company_id}: {err}")

def main():
    # --- Pre-run Checks ---
    if not all([DB_HOST, DB_USER, DB_PASS, DB_NAME]):
        print("Error: Database environment variables are not set.")
        return

    if not os.path.exists(MODEL_PATH):
        print(f"Error: Model file not found at '{MODEL_PATH}'")
        return

    if not os.path.isdir(DATA_DIR):
        print(f"Error: Data directory '{DATA_DIR}' not found.")
        return

    # --- Load Model ---
    try:
        model = joblib.load(MODEL_PATH)
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    # --- Database Connection ---
    db, cursor = None, None
    try:
        db = mysql.connector.connect(
            host=DB_HOST, port=DB_PORT, user=DB_USER, 
            password=DB_PASS, database=DB_NAME
        )
        cursor = db.cursor()
    except mysql.connector.Error as err:
        print(f"Database connection failed: {err}")
        return

    # --- Main Processing Loop ---
    print("Starting data processing and database insertion...")
    for filename in os.listdir(DATA_DIR):
        if not filename.endswith(".json"):
            continue

        company_id = filename.replace(".json", "")
        path = os.path.join(DATA_DIR, filename)

        try:
            features = extract_features(path)
            if not features:
                print(f"⚠️ Skipped {company_id}: could not extract features.")
                continue

            row = np.array(list(features.values())).reshape(1, -1)
            label = model.predict(row)[0]

            with open(path, 'r') as f:
                data = json.load(f)
            
            analysis_points = data.get("analysis", {}).get("points", [])
            pros, cons = pick_pros_cons(analysis_points)

            store_to_db(cursor, company_id, pros, cons, label)
            db.commit()

        except json.JSONDecodeError:
            print(f"❌ Failed for {company_id}: Invalid JSON.")
        except Exception as e:
            print(f"❌ An unexpected error occurred for {company_id}: {e}")

    # --- Cleanup ---
    if db and db.is_connected():
        cursor.close()
        db.close()
        print("\nDatabase connection closed.")
    
    print("🎉 All data processed.")

if __name__ == "__main__":
    main()
