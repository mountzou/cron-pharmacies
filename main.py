import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK
cred = credentials.Certificate("firebase_credentials.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Constants
URL = "https://fsa-efimeries.gr/"

# Function to scrape the data
def scrape_drug_stores():
    # Fetch the page
    response = requests.get(URL)
    response.raise_for_status()  # Raise an exception if the request was unsuccessful

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the table by id
    table = soup.find('table', id='table')

    if not table:
        raise ValueError("Could not find the table with id='table' on the page.")

    # Extract the headers
    headers = [header.text.strip() for header in table.find('thead').find_all('th')]
    headers = headers[:-1]  # Remove the "Κατάσταση" column

    # Extract the rows
    rows = table.find('tbody').find_all('tr')

    # List to hold the results
    drug_stores = []

    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= len(headers):
            # Create a dictionary for each drug store using header names as keys
            store_info = {
                headers[0]: cells[0].text.strip(),
                headers[1]: cells[1].text.strip(),
                headers[2]: cells[2].text.strip(),
                headers[3]: cells[3].text.strip(),
                headers[4]: cells[4].text.strip()
            }
            drug_stores.append(store_info)

    return headers, drug_stores

# Function to write data to CSV
def save_to_csv(headers, data):
    # Get today's date
    today = datetime.today().strftime('%Y-%m-%d')

    # Define the filename
    filename = f"drug_stores_on_duty_{today}.csv"

    # Write to CSV
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)

    print(f"Data successfully saved to {filename}")

# Function to write data to Firestore
def save_to_firestore(data):
    # Get today's date
    today = datetime.today().strftime('%Y-%m-%d')

    # Upload data to Firestore
    db.collection("drug_stores").document(today).set({"stores": data})
    print(f"Data successfully saved to Firestore under collection 'drug_stores' and document '{today}'.")

# Usage example
if __name__ == "__main__":
    headers, drug_stores_on_duty = scrape_drug_stores()
    save_to_csv(headers, drug_stores_on_duty)
    save_to_firestore(drug_stores_on_duty)
