import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv, find_dotenv

# پیدا کردن و لود فایل .env
dotenv_path = find_dotenv()
print(f"Path to .env file: {dotenv_path}")
load_dotenv(dotenv_path)

# گرفتن توکن از متغیر محیطی
TOKEN = os.getenv("BOT_TOKEN")
print("TOKEN:", TOKEN)  # برای تست مقدار توکن

CHANNEL_USERNAME = "@soosssis"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user.id)

    if member.status not in ["member", "creator", "administrator"]:
        keyboard = [[InlineKeyboardButton("عضویت در کانال", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("برای استفاده از ربات ابتدا در کانال عضو شوید:", reply_markup=reply_markup)
        return

    await update.message.reply_text("سلام! لطفاً یک عکس واضح از صورت خود بفرستید تا آنالیز آغاز شود.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    photo_file = await update.message.photo[-1].get_file()
    file_path = f"photos/{user.id}.jpg"
    os.makedirs("photos", exist_ok=True)
    await photo_file.download_to_drive(file_path)
    await update.message.reply_text("عکس شما با موفقیت دریافت شد. در حال پردازش...")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

if __name__ == "__main__":
    print("ربات در حال اجراست...")
    app.run_polling()
