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

def extract_features(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)

    company = data.get("company", {})
    analysis = data.get("analysis", {})
    profit = data.get("data", {}).get("profitandloss", [])
    balance = data.get("data", {}).get("balancesheet", [])

    # Basic fields
    roe = float(company.get("roe_percentage") or 0)
    sales_growth = float(analysis.get("sales_growth") or 0)
    dividend = float(analysis.get("dividend_payout") or 0)

    # Profit margin = net profit / sales
    try:
        latest = profit[-1] if profit else {}
        net_profit = float(latest.get("net_profit") or 1)
        sales = float(latest.get("sales") or 1)
        profit_margin = (net_profit / sales) * 100
    except:
        profit_margin = 0

    # Debt to Equity = borrowings / reserves
    try:
        latest_bal = balance[-1] if balance else {}
        borrowings = float(latest_bal.get("borrowings") or 0)
        reserves = float(latest_bal.get("reserves") or 1)
        debt_to_equity = borrowings / reserves
    except:
        debt_to_equity = 0

    return {
        "roe": roe,
        "sales_growth": sales_growth,
        "dividend": dividend,
        "profit_margin": profit_margin,
        "debt_to_equity": debt_to_equity
    }

def label_data(file_path):
    x = extract_features(file_path)
    if x["roe"] > 20 and x["sales_growth"] > 15 and x["profit_margin"] > 15:
        return "Strong"
    elif x["roe"] > 10 and x["sales_growth"] > 10:
        return "Moderate"
    else:
        return "Weak"

def main():
    X = []
    y = []

    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".json"):
            path = os.path.join(DATA_DIR, filename)
            try:
                features = extract_features(path)
                label = label_data(path)
                X.append(list(features.values()))
                y.append(label)
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    # Convert to numpy arrays
    X = np.array(X)
    y = np.array(y)

    # Train-Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # ML Pipeline with StandardScaler + RandomForest
    pipe = Pipeline([
        ('scaler', StandardScaler()),
        ('clf', RandomForestClassifier(n_estimators=100, random_state=42))
    ])

    pipe.fit(X_train, y_train)

    # Evaluate Model
    y_pred = pipe.predict(X_test)
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print(classification_report(y_test, y_pred))

    # Save the model
    joblib.dump(pipe, "model.joblib")
    print("✅ Model saved as model.joblib")

if __name__ == "__main__":
    main()
