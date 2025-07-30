import requests
import os
import pandas as pd
import time
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://bluemutualfund.in/server/api/company.php"
EXCEL_FILE = "company_id.xlsx"
SAVE_DATA = "data"

os.makedirs(SAVE_DATA, exist_ok=True)

def fetch_data(symbol):
    url = f"{BASE_URL}?id={symbol}&api_key={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data for {symbol}. Status code: {response.status_code}")
        return None       
    

def main():
    df = pd.read_excel(EXCEL_FILE)
    for symbol in df['company_id']:
        print(f"Fetching data for {symbol}...")
        data = fetch_data(symbol)   
        if data:
            with open(os.path.join(SAVE_DATA, f"{symbol}.json"), 'w') as f: 
                import json
                json.dump(data, f, indent=2)
        time.sleep(1)

if __name__ == "__main__":
    main()    
        
