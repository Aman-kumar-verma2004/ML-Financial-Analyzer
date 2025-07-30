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

DATA_DIR = "backend/data"   # ✅ सही path डालें

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
        analysis_text["pros"].append(f"✅ High ROE of {roe}%.")
    if roce > 15:
        analysis_text["pros"].append(f"✅ Excellent ROCE of {roce}%.")
    if book_value > 500:
        analysis_text["pros"].append(f"✅ High book value of {book_value} INR.")

    # ✅ Cons (Weak Points)
    if roe < 10:
        analysis_text["cons"].append(f"❌ Low ROE of {roe}%.")
    if roce < 10:
        analysis_text["cons"].append(f"❌ Weak ROCE of {roce}%.")
    if book_value < 100:
        analysis_text["cons"].append(f"❌ Very low book value of {book_value} INR.")

    # ✅ Labeling Logic
    if roe > 18 and roce > 18:
        strength = "Strong"
    elif roe > 10 or roce > 10:
        strength = "Moderate"
    else:
        strength = "Weak"

    # ✅ अगर pros/cons खाली हैं तो default add करें
    if not analysis_text["pros"]:
        analysis_text["pros"].append("No major strengths found.")
    if not analysis_text["cons"]:
        analysis_text["cons"].append("No major weaknesses found.")

    return analysis_text, strength


# ✅ Iterate through all JSON files
for file in os.listdir(DATA_DIR):
    if file.endswith(".json"):
        path = os.path.join(DATA_DIR, file)

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"❌ ERROR reading {file}: {e}")
            continue

        # ✅ अगर `company` key missing है → SKIP करें
        if "company" not in data:
            print(f"⚠️ SKIPPING {file} → No 'company' key found")
            continue

        company_id = data["company"].get("id", "").strip()
        company_name = data["company"].get("company_name", "").strip()

        insights, strength = analyze_company(data)

        pros_text = " | ".join(insights["pros"])
        cons_text = " | ".join(insights["cons"])

        # ✅ Update MySQL Table with pros, cons, and strength
        query = """
        UPDATE ml 
        SET pros = %s, cons = %s, strngth = %s 
        WHERE company = %s
        """
        values = (pros_text, cons_text, strength, company_id)

        try:
            cursor.execute(query, values)
            print(f"✅ {company_name} → {strength} updated")
        except Exception as e:
            print(f"❌ Error for {company_name}: {e}")

# ✅ Commit changes
db.commit()
cursor.close()
db.close()
print("🎯 ML Analysis Completed & Data Stored in DB")
