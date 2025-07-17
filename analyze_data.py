import os
import json
import joblib
import numpy as np

MODEL_PATH = "model.joblib"
DATA_DIR = "data"

# Load trained model
model = joblib.load(MODEL_PATH)

# Same feature extractor used during training
def extract_features(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)

    company = data.get("company", {})
    analysis = data.get("analysis", {})
    profit = data.get("data", {}).get("profitandloss", [])
    balance = data.get("data", {}).get("balancesheet", [])

    roe = float(company.get("roe_percentage", 0))
    sales_growth = float(analysis.get("sales_growth", 0))
    dividend = float(analysis.get("dividend_payout", 0))

    try:
        latest = profit[-1] if profit else {}
        net_profit = float(latest.get("net_profit", 1))
        sales = float(latest.get("sales", 1))
        profit_margin = (net_profit / sales) * 100
    except:
        profit_margin = 0

    try:
        latest_bal = balance[-1] if balance else {}
        borrowings = float(latest_bal.get("borrowings", 0))
        reserves = float(latest_bal.get("reserves", 1))
        debt_to_equity = borrowings / reserves
    except:
        debt_to_equity = 0

    return [
        roe,
        sales_growth,
        dividend,
        profit_margin,
        debt_to_equity
    ]

def main():
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".json"):
            file_path = os.path.join(DATA_DIR, filename)
            try:
                features = extract_features(file_path)
                pred = model.predict([features])[0]

                symbol = filename.replace(".json", "")
                print(f"{symbol} → {pred}")
            except Exception as e:
                print(f"Failed for {filename}: {e}")

if __name__ == "__main__":
    main()
