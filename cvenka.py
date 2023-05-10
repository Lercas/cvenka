import requests
import time
from telegram import Bot

NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/1.0"
EXPLOIT_DB_API_URL = "https://api.exploit-db.com/search"
TELEGRAM_TOKEN = "YOUR_TELEGRAM_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"
API_KEY = "YOUR_API_KEY"

def fetch_vulnerabilities(start_date, end_date):
    params = {
        "modStartDate": start_date,
        "modEndDate": end_date
    }
    response = requests.get(NVD_API_URL, params=params)
    if response.status_code == 200:
        return response.json()["result"]["CVE_Items"]
    else:
        print(f"Error: {response.status_code}")
        return []

def fetch_exploits(start_date, end_date):
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    params = {
        "modified_after": start_date,
        "modified_before": end_date
    }
    response = requests.get(EXPLOIT_DB_API_URL, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()["data"]
    else:
        print(f"Error: {response.status_code}")
        return []

def send_message(text: str):
    bot = Bot(token=TELEGRAM_TOKEN)
    bot.send_message(chat_id=CHAT_ID, text=text)

def search_vulnerabilities(keyword):
    current_date = time.strftime("%Y-%m-%d")
    start_date = f"{current_date}T00:00:00:000 UTC-05:00"
    end_date = f"{current_date}T23:59:59:000 UTC-05:00"

    vulnerabilities = fetch_vulnerabilities(start_date, end_date)
    exploits = fetch_exploits(current_date, current_date)

    results = []

    for vulnerability in vulnerabilities:
        if keyword.lower() in vulnerability["cve"]["description"]["description_data"][0]["value"].lower():
            results.append(vulnerability)

    for exploit in exploits:
        if keyword.lower() in exploit["title"].lower():
            results.append(exploit)

    return results

def main():
    while True:
        current_date = time.strftime("%Y-%m-%d")
        start_date = f"{current_date}T00:00:00:000 UTC-05:00"
        end_date = f"{current_date}T23:59:59:000 UTC-05:00"

        vulnerabilities = fetch_vulnerabilities(start_date, end_date)
        for vulnerability in vulnerabilities:
            message = f"{vulnerability['cve']['CVE_data_meta']['ID']}\n{vulnerability['cve']['description']['description_data'][0]['value']}"
            send_message(message)

        exploits = fetch_exploits(current_date, current_date)
        for exploit in exploits:
            message = f"{exploit['id']}\n{exploit['title']}"
            send_message(message)

        time.sleep(3600)

if __name__ == "__main__":
    main()
