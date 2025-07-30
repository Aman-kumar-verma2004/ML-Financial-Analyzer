import os
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib

DATA_DIR = "data"
MODEL_FILE = "model.joblib"

def safe_float(value, default=0.0):
    """Safely convert a value to float, returning a default if conversion fails."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def extract_features(file_path):
    """Extracts features from a JSON file, handling missing or malformed data."""
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

def label_data(features):
    """Labels the data based on extracted features."""
    if (
        features["roe"] > 15 and 
        features["sales_growth"] > 10 and 
        features["profit_margin"] > 10
    ):
        return "Strong"
    elif (
        features["roe"] > 8 and 
        features["sales_growth"] > 5 and 
        features["profit_margin"] > 5
    ):
        return "Moderate"
    else:
        return "Weak"

def main():
    if not os.path.isdir(DATA_DIR):
        print(f"Error: Data directory '{DATA_DIR}' not found.")
        return

    X = []
    y = []
    filenames = []

    print(f"Processing files in '{DATA_DIR}'...")
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".json"):
            path = os.path.join(DATA_DIR, filename)
            try:
                features = extract_features(path)
                label = label_data(features)
                X.append(list(features.values()))
                y.append(label)
                filenames.append(filename)
            except json.JSONDecodeError:
                print(f"Skipping {filename}: Invalid JSON format.")
            except Exception as e:
                print(f"An error occurred while processing {filename}: {e}")

    if not X:
        print("No valid data found to train the model.")
        return

    X = np.array(X)
    y = np.array(y)

    if len(X) < 2:
        print("Not enough data to perform a train-test split.")
        return

    # Train-Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # ML Pipeline
    pipe = Pipeline([
        ('scaler', StandardScaler()),
        ('clf', RandomForestClassifier(n_estimators=100, random_state=42))
    ])

    print("
Training the model...")
    pipe.fit(X_train, y_train)

    # Evaluate Model
    print("
Evaluating the model...")
    y_pred = pipe.predict(X_test)
    
    # Ensure there are predicted samples to evaluate
    if y_test.size > 0:
        print("Accuracy:", accuracy_score(y_test, y_pred))
        print("Classification Report:")
        print(classification_report(y_test, y_pred))
    else:
        print("No test data to evaluate.")

    # Save the model
    try:
        joblib.dump(pipe, MODEL_FILE)
        print(f"
✅ Model saved successfully as {MODEL_FILE}")
    except IOError as e:
        print(f"Error saving model: {e}")

if __name__ == "__main__":
    main()
