import os
import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputFile
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# ================== ADD TOKEN HERE ==================
TOKEN = "8549339978:AAGYWiZsMa8LJKRF0f95tZPkUewefpixvDc"
# ====================================================

ADMIN_CHAT_ID = 1891081482   # <-- put your numeric Telegram ID here
UPI_ID = "aijazruler27@okaxis"
ADMIN_USERNAME = "@aijazruler"

QR_FILENAME = "upi.png"  # Make sure this file exists in root folder


PRODUCTS = {
    "🎧 Spotify Panel Root": ["7 Days — $3.80", "15 Days — $5.50", "30 Days — $10.00", "60 Days — $20.00"],
    "🎮 Stricks BR Root": ["1 Day — $2.00", "3 Days — $3.00", "5 Days — $5.00", "7 Days — $5.00", "10 Days — $7.00", "30 Days — $15.00"],
    "🔥 Drip Client APK Mod": ["1 Day — $1.90", "7 Days — $5.00", "15 Days — $10.00", "30 Days — $10.00"],
    "⚡ HG APK Mod + Root": ["1 Day — $2.50", "10 Days — $5.50", "30 Days — $15.00"],
    "💎 Haxx Cker Pro": ["10 Days — $10.00", "20 Days — $15.00", "30 Days — $20.00"],
    "🚀 PatoTeam APK Mod": ["1 Day — $2.70", "3 Days — $3.40", "7 Days — $5.00", "15 Days — $10.00", "30 Days — $20.00"],
    "⭐ Prime APK Mod": ["5 Days — $3.00", "10 Days — $5.00"]
}


# ================= START =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(product, callback_data=f"product|{product}")]
        for product in PRODUCTS.keys()
    ]

    await update.message.reply_text(
        "🔥 Welcome to Premium Panel Store!\n\nSelect Product:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ================= PRODUCT SELECT =================

async def product_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, product_name = query.data.split("|", 1)
    context.user_data["product"] = product_name

    keyboard = [
        [InlineKeyboardButton(duration, callback_data=f"duration|{duration}")]
        for duration in PRODUCTS[product_name]
    ]

    await query.edit_message_text(
        f"✅ Selected: {product_name}\n\nChoose Duration:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ================= DURATION SELECT =================

async def duration_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, duration = query.data.split("|", 1)

    # 🔥 Auto price detection
    price = duration.split("$")[1].strip()

    context.user_data["duration"] = duration
    context.user_data["price"] = price

    product = context.user_data["product"]

    caption_text = (
        f"🛒 Product: {product}\n"
        f"⏳ Duration: {duration}\n"
        f"💰 Amount: ${price}\n\n"
        f"🏦 UPI ID: {UPI_ID}\n\n"
        f"📌 Scan QR or Pay Manually\n"
        f"📸 After payment, send screenshot here.\n\n"
        f"⚠ After payment mention {ADMIN_USERNAME}"
    )

    # Send QR Image
    if os.path.exists(QR_FILENAME):
        with open(QR_FILENAME, "rb") as photo:
            await query.message.reply_photo(photo=photo, caption=caption_text)
    else:
        await query.message.reply_text("❌ QR file 'upi.png' not found in root folder.")

# ================= SCREENSHOT HANDLER =================

async def screenshot_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    product = context.user_data.get("product", "Unknown")
    duration = context.user_data.get("duration", "Unknown")
    price = context.user_data.get("price", "Unknown")

    caption = (
        f"📥 New Payment Screenshot\n\n"
        f"👤 User: @{user.username}\n"
        f"🛒 Product: {product}\n"
        f"⏳ Duration: {duration}\n"
        f"💰 Amount: ${price}"
    )

    await update.message.forward(chat_id=ADMIN_CHAT_ID)
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=caption)

    await update.message.reply_text(
        "✅ Screenshot received!\n⏳ Admin will verify soon."
    )


# ================= MAIN =================

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(product_selected, pattern="^product"))
    app.add_handler(CallbackQueryHandler(duration_selected, pattern="^duration"))
    app.add_handler(MessageHandler(filters.PHOTO, screenshot_handler))

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()