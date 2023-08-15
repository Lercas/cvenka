import requests
import time
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext

NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/1.0"
EXPLOIT_DB_API_URL = "https://api.exploit-db.com/search"
#И вот не понятно, портал закрыли или работает только платно
#VULN_DB_API_URL = "https://vulndb.com/?api" 
TELEGRAM_TOKEN = "YOUR_TELEGRAM_TOKEN"
API_KEY = "YOUR_API_KEY"


def fetch_data(url, headers=None, params=None):
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None


def fetch_vulnerabilities(start_date, end_date):
    params = {
        "modStartDate": start_date,
        "modEndDate": end_date
    }
    data = fetch_data(NVD_API_URL, params=params)
    return data["result"]["CVE_Items"] if data else []


def fetch_exploits(start_date, end_date):
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    params = {
        "modified_after": start_date,
        "modified_before": end_date
    }
    data = fetch_data(EXPLOIT_DB_API_URL, headers=headers, params=params)
    return data["data"] if data else []


def send_message(chat_id: str, text: str):
    bot = Bot(token=TELEGRAM_TOKEN)
    bot.send_message(chat_id=chat_id, text=text)


def set_keywords(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    user_keywords[user_id] = context.args
    update.message.reply_text(f"Keywords updated: {', '.join(user_keywords[user_id])}")


def start_bot():
    updater = Updater(TELEGRAM_TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("set_keywords", set_keywords))
    updater.start_polling()
    updater.idle()


user_keywords = {}


def check_vulnerability_keywords(item, keywords):    
    for keyword in keywords:
        if keyword.lower() in item.lower():
            return True

            
    return False


def main():
    start_bot()

    while True:
        current_date = time.strftime("%Y-%m-%d")
        start_date = f"{current_date}T00:00:00:000 UTC-05:00"
        end_date = f"{current_date}T23:59:59:000 UTC-05:00"

        vulnerabilities = fetch_vulnerabilities(start_date, end_date)
        exploits = fetch_exploits(current_date, current_date)

        for user_id, keywords in user_keywords.items():
            for vulnerability in vulnerabilities:
                description = vulnerability["cve"]["description"]["description_data"][0]["value"]
                if check_vulnerability_keywords(description, keywords):
                    message = f"{vulnerability['cve']['CVE_data_meta']['ID']}\n{description}"
                    send_message(chat_id=user_id, text=message)

            for exploit in exploits:
                title = exploit["title"]
                if check_vulnerability_keywords(title, keywords):
                    message = f"{exploit['id']}\n{title}"
                    send_message(chat_id=user_id, text=message)

        time.sleep(3600)


if __name__ == "__main__":
    main()
