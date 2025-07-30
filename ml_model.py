import os
import json
import mysql.connector

# ✅ MySQL Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="ml_analysis"
)
cursor = db.cursor()

# ✅ Fix Path (backend/data ke andar JSON files)
DATA_DIR = os.path.join(os.path.dirname(__file__), "backend", "data")

def analyze_company(data):
    """ 🔍 Analyze financial data & generate Pros and Cons """
    company = data.get("company", {})
    analysis_text = {"pros": [], "cons": []}

    try:
        roe = float(company.get("roe_percentage", 0))
        roce = float(company.get("roce_percentage", 0))
        book_value = float(company.get("book_value", 0))
    except:
        roe = roce = book_value = 0

    # ✅ Pros (Strong Points)
    if roe > 15:
        analysis_text["pros"].append(f"Company has a strong Return on Equity (ROE) of {roe}%.")
    if roce > 15:
        analysis_text["pros"].append(f"Company shows excellent Return on Capital Employed (ROCE) of {roce}%.")
    if book_value > 500:
        analysis_text["pros"].append(f"Company has a high book value of {book_value} INR.")

    # ✅ Cons (Weak Points)
    if roe < 10:
        analysis_text["cons"].append(f"Company has a low Return on Equity (ROE) of only {roe}%.")
    if roce < 10:
        analysis_text["cons"].append(f"Company has a weak ROCE of {roce}%.")
    if book_value < 100:
        analysis_text["cons"].append(f"Company has a very low book value of {book_value} INR.")

    # ✅ If no Pros/Cons found
    if not analysis_text["pros"]:
        analysis_text["pros"].append("No strong positive indicators found.")
    if not analysis_text["cons"]:
        analysis_text["cons"].append("No major weaknesses detected.")

    return analysis_text

# ✅ Iterate through all JSON files in backend/data
for file in os.listdir(DATA_DIR):
    if file.endswith(".json"):
        path = os.path.join(DATA_DIR, file)

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

            # ✅ 🚨 SAFETY CHECK: Agar 'company' key missing hai, skip file
            if "company" not in data:
                print(f"⚠️ Skipping {file} → 'company' key missing.")
                continue

            company_id = data["company"].get("id", "").strip()
            company_name = data["company"].get("company_name", "").strip()

            insights = analyze_company(data)

            pros_text = " | ".join(insights["pros"])
            cons_text = " | ".join(insights["cons"])

            # ✅ Update MySQL Table
            query = """
            UPDATE ml 
            SET pros = %s, cons = %s 
            WHERE company = %s
            """
            values = (pros_text, cons_text, company_id)

            try:
                cursor.execute(query, values)
                print(f"✅ {company_name} → Pros & Cons Updated")
            except Exception as e:
                print(f"❌ Error for {company_name}: {e}")

# ✅ Commit changes
db.commit()
cursor.close()
db.close()
print("🎯 ML Analysis Completed & Data Stored in DB")
