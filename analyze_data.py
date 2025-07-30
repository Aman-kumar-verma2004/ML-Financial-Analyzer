import os
import json
import joblib
import numpy as np

MODEL_PATH = "model.joblib"
DATA_DIR = "data"
RESULTS_FILE = "analysis_results.json"

# Load trained model
try:
    model = joblib.load(MODEL_PATH)
except FileNotFoundError:
    print(f"Error: Model file not found at {MODEL_PATH}")
    exit(1)
except Exception as e:
    print(f"Error loading model: {e}")
    exit(1)

def extract_features(file_path):
    """Extracts features from a JSON file, handling missing data."""
    with open(file_path, 'r') as f:
        data = json.load(f)

    company = data.get("company", {})
    analysis = data.get("analysis", {})
    profit = data.get("data", {}).get("profitandloss", [])
    balance = data.get("data", {}).get("balancesheet", [])

    def safe_float(value, default=0.0):
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    roe = safe_float(company.get("roe_percentage"))
    sales_growth = safe_float(analysis.get("sales_growth"))
    dividend = safe_float(analysis.get("dividend_payout"))

    profit_margin = 0.0
    if profit:
        latest = profit[-1]
        net_profit = safe_float(latest.get("net_profit"))
        sales = safe_float(latest.get("sales"))
        if sales > 0:
            profit_margin = (net_profit / sales) * 100

    debt_to_equity = 0.0
    if balance:
        latest_bal = balance[-1]
        borrowings = safe_float(latest_bal.get("borrowings"))
        reserves = safe_float(latest_bal.get("reserves"))
        if reserves > 0:
            debt_to_equity = borrowings / reserves

    return [
        roe,
        sales_growth,
        dividend,
        profit_margin,
        debt_to_equity
    ]

def main():
    if not os.path.isdir(DATA_DIR):
        print(f"Error: Data directory '{DATA_DIR}' not found.")
        return

    results = {}
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".json"):
            file_path = os.path.join(DATA_DIR, filename)
            symbol = filename.replace(".json", "")
            try:
                features = extract_features(file_path)
                # Scikit-learn models expect a 2D array
                features_array = np.array(features).reshape(1, -1)
                prediction = model.predict(features_array)[0]
                
                # Convert numpy types to native Python types for JSON serialization
                if isinstance(prediction, np.generic):
                    prediction = prediction.item()

                results[symbol] = prediction
                print(f"{symbol} → {prediction}")

            except json.JSONDecodeError:
                print(f"Skipping {filename}: Invalid JSON format.")
            except Exception as e:
                print(f"An error occurred while processing {filename}: {e}")

    try:
        with open(RESULTS_FILE, 'w') as f:
            json.dump(results, f, indent=4)
        print(f"Analysis complete. Results saved to {RESULTS_FILE}")
    except IOError as e:
        print(f"Error writing results to {RESULTS_FILE}: {e}")


if __name__ == "__main__":
    main()
