import requests
import os
from dotenv import load_dotenv

load_dotenv()

def set_webhook():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")
    
    # Telegram API endpoint for setting webhook
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
    
    # Data to send
    data = {
        "url": f"{WEBHOOK_URL}/webhook",
        "allowed_updates": ["message", "callback_query"]
    }
    
    # Send request to Telegram
    response = requests.post(url, json=data)
    
    # Print result
    if response.status_code == 200:
        print("Webhook set successfully!")
        print(response.json())
    else:
        print("Failed to set webhook")
        print(response.text)

    # Get current webhook info
    info_response = requests.get(f"https://api.telegram.org/bot{TOKEN}/getWebhookInfo")
    print("\nCurrent Webhook Info:")
    print(info_response.json())

if __name__ == "__main__":
    set_webhook() 