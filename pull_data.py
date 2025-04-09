import json
import os
import requests
import pandas as pd
from datetime import datetime

# Load token from file
with open("token.json") as f:
    token = json.load(f)

access_token = token["access_token"]
realm_id = token["realm_id"]
base_url = "https://quickbooks.api.intuit.com"
headers = {
    "Authorization": f"Bearer {access_token}",
    "Accept": "application/json"
}

def fetch_report(report_name, params={}):
    """Fetch accounting reports like TrialBalance, GeneralLedger, etc."""
    url = f"{base_url}/v3/company/{realm_id}/reports/{report_name}"
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        print(f"✅ {report_name} report pulled")
        return response.json()
    else:
        print(f"❌ Failed to get {report_name}: {response.status_code}")
        print(response.text)
        return None

def fetch_entities(entity_type, params={}):
    """Fetch transactional entities like invoice, bill, journalentry, etc."""
    url = f"{base_url}/v3/company/{realm_id}/{entity_type}"
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        print(f"✅ {entity_type} pulled")
        return response.json()
    else:
        print(f"❌ Failed to get {entity_type}: {response.status_code}")
        print(response.text)
        return None

def save_to_csv(data, filename, data_key=None):
    """Save raw JSON data to CSV. Supports nested keys (e.g., QueryResponse > Invoice)."""
    if data_key:
        records = data.get("QueryResponse", {}).get(data_key, [])
    else:
        records = data.get("Rows", [])

    if not records:
        print(f"⚠️ No records found in {filename}")
        return

    df = pd.json_normalize(records)
    os.makedirs("output", exist_ok=True)
    output_path = f"output/{filename}.csv"
    df.to_csv(output_path, index=False)
    print(f"📁 Saved to {output_path}")

if __name__ == "__main__":
    # Example fetches
    trial_balance = fetch_report("TrialBalance", {"minorversion": "65"})
    save_to_csv(trial_balance, "trial_balance")

    general_ledger = fetch_report("GeneralLedger", {
        "minorversion": "65",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31"
    })
    save_to_csv(general_ledger, "general_ledger")

    invoices = fetch_entities("invoice", {"minorversion": "65"})
    save_to_csv(invoices, "invoices", data_key="Invoice")

    journal_entries = fetch_entities("journalentry", {"minorversion": "65"})
    save_to_csv(journal_entries, "journal_entries", data_key="JournalEntry")

