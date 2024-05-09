import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("firebase_credentials.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

URL = "https://fsa-efimeries.gr/"

def scrape_drug_stores():
    response = requests.get(URL)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    table = soup.find('table', id='table')

    if not table:
        raise ValueError("Could not find the table with id='table' on the page.")

    headers = [header.text.strip() for header in table.find('thead').find_all('th')]
    headers = headers[:-1]

    rows = table.find('tbody').find_all('tr')

    drug_stores = []

    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= len(headers):
            store_info = {
                headers[0]: cells[0].text.strip(),
                headers[1]: cells[1].text.strip(),
                headers[2]: cells[2].text.strip(),
                headers[3]: cells[3].text.strip(),
                headers[4]: cells[4].text.strip(),
                headers[5]: cells[5].text.strip(),
                headers[6]: cells[6].text.strip()
            }
            drug_stores.append(store_info)

    return headers, drug_stores

def save_to_firestore(data):
    today = datetime.today().strftime('%Y-%m-%d')

    db.collection("drug_stores").document(today).set({"stores": data})
    print(f"Data successfully saved to Firestore under collection 'drug_stores' and document '{today}'.")

if __name__ == "__main__":
    headers, drug_stores_on_duty = scrape_drug_stores()
    save_to_firestore(drug_stores_on_duty)
