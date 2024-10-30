from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from flask import Flask, request
from quart import Quart, request, Response
import random
import datetime
import os
from dotenv import load_dotenv
import hmac
import hashlib

# Load environment variables
load_dotenv()

# Initialize Quart app (async Flask)
app = Quart(__name__)

# Atbash conversion dictionary for Hebrew letters
ATBASH_DICT = {
    'א': 'ת', 'ב': 'ש', 'ג': 'ר', 'ד': 'ק', 'ה': 'צ', 'ו': 'פ',
    'ז': 'ע', 'ח': 'ס', 'ט': 'נ', 'י': 'מ', 'כ': 'ל', 'ל': 'כ',
    'מ': 'י', 'נ': 'ט', 'ס': 'ח', 'ע': 'ז', 'פ': 'ו', 'צ': 'ה',
    'ק': 'ד', 'ר': 'ג', 'ש': 'ב', 'ת': 'א',
    'ך': 'ל', 'ם': 'י', 'ן': 'ט', 'ף': 'ו', 'ץ': 'ה'
}

# Fun facts about ancient Hebrew and codes
FUN_FACTS = [
    "שפת אתבש הייתה אחת משיטות ההצפנה הראשונות בהיסטוריה!",
    "בספר ירמיהו בתנ״ך, המילה 'ששך' היא למעשה 'בבל' בצופן אתבש",
    "הגימטריה היא שיטת קידוד עתיקה נוספת בעברית",
    "צופן אתבש הוא דוגמה לצופן החלפה חד-אלפביתי",
    "בימי בית המקדש השתמשו בצפנים שונים להעברת מסרים"
]

# Create bot application at module level
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("No token found! Make sure to set TELEGRAM_BOT_TOKEN in .env file")

# Initialize application properly
application = Application.builder().token(TOKEN).build()

# Add secret token as constant
WEBHOOK_SECRET_TOKEN = "your_secret_token"  # Should match the one in set_webhook.py

@app.route('/health')
async def health_check():
    """Health check endpoint"""
    return "Bot is running"

@app.route('/webhook', methods=['POST'])
async def webhook():
    """Handle incoming webhook updates with proper security and error handling"""
    try:
        # Verify the request is from Telegram
        secret_header = request.headers.get('X-Telegram-Bot-Api-Secret-Token')
        if WEBHOOK_SECRET_TOKEN and secret_header != WEBHOOK_SECRET_TOKEN:
            return Response('Unauthorized', status=403)

        # Get and validate the update data
        update_data = await request.get_json()
        if not update_data:
            return Response('Invalid update data', status=400)

        # Create Update object and process it
        try:
            update = Update.de_json(update_data, application.bot)
            await application.process_update(update)
        except Exception as e:
            print(f"Error processing update: {e}")
            # Don't return error to Telegram - they might retry bad updates
            return Response('OK', status=200)

        return Response('OK', status=200)

    except Exception as e:
        print(f"Webhook error: {e}")
        return Response('Internal server error', status=500)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message with main menu when the command /start is issued."""
    keyboard = [
        [InlineKeyboardButton("🔄 המר טקסט לאתבש", callback_data='convert')],
        [InlineKeyboardButton("❓ עובדה מעניינת", callback_data='fact')],
        [InlineKeyboardButton("🎲 משחק ניחושים", callback_data='game')],
        [InlineKeyboardButton("📊 סטטיסטיקות", callback_data='stats')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        'ברוך הבא לבוט האתבש המתקדם! 🎉\n'
        'בחר אחת מהאפשרויות הבאות:',
        reply_markup=reply_markup
    )

def convert_to_atbash(text: str) -> str:
    """Convert Hebrew text to Atbash."""
    result = ''
    for char in text:
        if char in ATBASH_DICT:
            result += ATBASH_DICT[char]
        else:
            result += char
    return result

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages and respond with Atbash conversion."""
    text = update.message.text
    
    # Update user statistics
    user_id = update.effective_user.id
    if 'user_stats' not in context.bot_data:
        context.bot_data['user_stats'] = {}
    if user_id not in context.bot_data['user_stats']:
        context.bot_data['user_stats'][user_id] = {'messages': 0, 'chars': 0}
    
    context.bot_data['user_stats'][user_id]['messages'] += 1
    context.bot_data['user_stats'][user_id]['chars'] += len(text)

    # Convert text and create response keyboard
    atbash_text = convert_to_atbash(text)
    keyboard = [
        [InlineKeyboardButton("♻️ המר שוב", callback_data='convert')],
        [InlineKeyboardButton("📝 הסבר על התהליך", callback_data='explain')],
        [InlineKeyboardButton("📊 הסטטיסטיקות שלי", callback_data='stats')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"הטקסט באתבש:\n{atbash_text}\n\nמה תרצה לעשות עכשיו?",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()

    if query.data == 'fact':
        fact = random.choice(FUN_FACTS)
        await query.message.reply_text(f"💡 {fact}")
    
    elif query.data == 'game':
        # Start a guessing game
        original_word = random.choice(['שלום', 'תודה', 'אהבה', 'שמחה', 'חיים'])
        context.user_data['game_word'] = original_word
        atbash_word = convert_to_atbash(original_word)
        await query.message.reply_text(
            f"🎮 משחק ניחושים!\n"
            f"המילה באתבש היא: {atbash_word}\n"
            "נסה לנחש את המילה המקורית!"
        )
    
    elif query.data == 'stats':
        user_id = update.effective_user.id
        if 'user_stats' in context.bot_data and user_id in context.bot_data['user_stats']:
            stats = context.bot_data['user_stats'][user_id]
            await query.message.reply_text(
                f"📊 הסטטיסטיקות שלך:\n"
                f"מספר הודעות: {stats['messages']}\n"
                f"מספר תווים: {stats['chars']}\n"
                f"תאריך: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
        else:
            await query.message.reply_text("עדיין אין לך סטטיסטיקות 😊")
    
    elif query.data == 'explain':
        await query.message.reply_text(
            "🔍 איך עובד צופן אתבש?\n"
            "כל אות מוחלפת באות המקבילה לה מסוף האלפבית:\n"
            "א ⟷ ת\n"
            "ב ⟷ ש\n"
            "ג ⟷ ר\n"
            "וכן הלאה..."
        )

async def handle_game_guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle game guesses."""
    if 'game_word' in context.user_data:
        guess = update.message.text
        correct_word = context.user_data['game_word']
        
        if guess == correct_word:
            await update.message.reply_text("🎉 כל הכבוד! ניחשת נכון!")
            del context.user_data['game_word']
        else:
            await update.message.reply_text("❌ לא נכון, נסה שוב!")

async def init_webhook():
    """Initialize webhook settings with proper error handling"""
    try:
        WEBHOOK_URL = os.getenv("WEBHOOK_URL")
        if not WEBHOOK_URL:
            raise ValueError("No webhook URL found! Make sure to set WEBHOOK_URL in .env file")
        
        # Delete existing webhook first
        await application.bot.delete_webhook()
        
        # Set new webhook with all security options
        await application.bot.set_webhook(
            url=f"{WEBHOOK_URL}/webhook",
            allowed_updates=["message", "callback_query"],
            secret_token=WEBHOOK_SECRET_TOKEN,
            drop_pending_updates=True
        )
        
        # Verify webhook was set correctly
        webhook_info = await application.bot.get_webhook_info()
        print(f"Webhook set to {webhook_info.url}")
        if webhook_info.last_error_date:
            print(f"Warning: Last webhook error: {webhook_info.last_error_message}")

    except Exception as e:
        print(f"Failed to initialize webhook: {e}")
        raise

def main():
    """Start the bot with proper configuration."""
    PORT = int(os.getenv("PORT", 8443))
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_game_guess))

    # Initialize webhook before starting
    app.before_serving(init_webhook)
    
    # Configure Quart for production
    app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024  # 1MB max-limit
    
    # Start Quart server with proper host binding
    app.run(
        host='0.0.0.0',
        port=PORT,
        debug=False  # Important: set to False in production
    )

if __name__ == '__main__':
    main() 