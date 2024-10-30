from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import random
import datetime
import re
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

def main():
    """Start the bot."""
    # Get token from environment variable
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not TOKEN:
        raise ValueError("No token found! Make sure to set TELEGRAM_BOT_TOKEN in .env file")
    
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 