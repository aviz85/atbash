import requests
import os
from dotenv import load_dotenv

load_dotenv()

def set_webhook():
    """Set webhook for Telegram bot using official API"""
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")
    
    if not TOKEN:
        raise ValueError("No token found! Make sure to set TELEGRAM_BOT_TOKEN in .env file")
    if not WEBHOOK_URL:
        raise ValueError("No webhook URL found! Make sure to set WEBHOOK_URL in .env file")

    # Telegram API endpoint for webhook operations
    base_url = f"https://api.telegram.org/bot{TOKEN}"
    
    # First, delete any existing webhook
    delete_response = requests.get(f"{base_url}/deleteWebhook")
    print("Deleting old webhook:", delete_response.json())

    # Set the new webhook
    webhook_data = {
        "url": f"{WEBHOOK_URL}/webhook",
        "allowed_updates": ["message", "callback_query"],
        "drop_pending_updates": True,
        "secret_token": "your_secret_token"  # Optional but recommended for security
    }
    
    set_response = requests.post(
        f"{base_url}/setWebhook",
        json=webhook_data
    )
    
    # Get and print webhook info
    info_response = requests.get(f"{base_url}/getWebhookInfo")
    
    print("\n=== Webhook Setup Results ===")
    print("Set Webhook Response:", set_response.json())
    print("\nCurrent Webhook Info:", info_response.json())
    
    # Check if setup was successful
    if set_response.status_code == 200 and set_response.json().get("ok"):
        print("\n✅ Webhook set successfully!")
    else:
        print("\n❌ Failed to set webhook")

if __name__ == "__main__":
    set_webhook()