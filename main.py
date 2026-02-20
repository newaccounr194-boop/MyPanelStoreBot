import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ================= CONFIG =================
TOKEN = os.getenv("TOKEN")  # Token from Render environment variable
ADMIN_CHAT_ID = 1891081482  # Your numeric Telegram ID
UPI_ID = "aijazruler27@okaxis"
ADMIN_USERNAME = "@aijazruler"
QR_FILE = "upi.png"
# ==========================================

PRODUCTS = {
    "🎧 Spotify Panel Root": ["7 Days — $3.80", "15 Days — $5.50", "30 Days — $10.00", "60 Days — $20.00"],
    "🎮 Stricks BR Root": ["1 Day — $2.00", "3 Days — $3.00", "5 Days — $5.00", "7 Days — $5.00", "10 Days — $7.00", "30 Days — $15.00"],
    "🔥 Drip Client APK Mod": ["1 Day — $1.90", "7 Days — $5.00", "15 Days — $10.00", "30 Days — $10.00"],
    "⚡ HG APK Mod + Root": ["1 Day — $2.50", "10 Days — $5.50", "30 Days — $15.00"],
    "💎 Haxx Cker Pro": ["10 Days — $10.00", "20 Days — $15.00", "30 Days — $20.00"],
    "🚀 PatoTeam APK Mod": ["1 Day — $2.70", "3 Days — $3.40", "7 Days — $5.00", "15 Days — $10.00", "30 Days — $20.00"],
    "⭐ Prime APK Mod": ["5 Days — $3.00", "10 Days — $5.00"]
}

# ================= TELEGRAM BOT =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(p, callback_data=f"prod|{p}")]
                for p in PRODUCTS.keys()]
    await update.message.reply_text(
        "🔥 Select Product:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def product_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    product = query.data.split("|")[1]
    context.user_data["product"] = product

    keyboard = [[InlineKeyboardButton(d, callback_data=f"dur|{d}")]
                for d in PRODUCTS[product]]

    await query.edit_message_text(
        f"✅ Selected: {product}\n\nSelect Duration:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def duration_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    duration = query.data.split("|")[1]
    price = duration.split("$")[1].strip()

    context.user_data["duration"] = duration
    context.user_data["price"] = price

    product = context.user_data["product"]

    caption = (
        f"🛒 Product: {product}\n"
        f"⏳ Duration: {duration}\n"
        f"💰 Amount: ${price}\n\n"
        f"🏦 UPI ID: {UPI_ID}\n\n"
        f"📸 Send payment screenshot after paying.\n"
        f"⚠ Mention {ADMIN_USERNAME} after payment."
    )

    if os.path.exists(QR_FILE):
        with open(QR_FILE, "rb") as photo:
            await query.message.reply_photo(photo=photo, caption=caption)
    else:
        await query.message.reply_text("QR file not found.")

async def screenshot_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    product = context.user_data.get("product", "Unknown")
    duration = context.user_data.get("duration", "Unknown")
    price = context.user_data.get("price", "Unknown")

    await update.message.forward(chat_id=ADMIN_CHAT_ID)
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"📥 New Payment\nUser: @{user.username}\nProduct: {product}\nDuration: {duration}\nAmount: ${price}"
    )

    await update.message.reply_text("✅ Screenshot sent to admin.")

def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(product_handler, pattern="^prod"))
    app.add_handler(CallbackQueryHandler(duration_handler, pattern="^dur"))
    app.add_handler(MessageHandler(filters.PHOTO, screenshot_handler))
    app.run_polling()

# ================= FLASK SERVER FOR RENDER =================

flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)

# Run both
threading.Thread(target=run_bot).start()
run_web()
