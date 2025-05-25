
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from deepface import DeepFace
import os
import sqlite3

# تنظیمات لاگ‌ها
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# دیتابیس برای VIP
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS vip_users (user_id INTEGER PRIMARY KEY)")
conn.commit()

# توکن ربات را اینجا وارد کن
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# بررسی VIP بودن
def is_vip(user_id):
    cursor.execute("SELECT * FROM vip_users WHERE user_id = ?", (user_id,))
    return cursor.fetchone() is not None

# شروع ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! 👋\nلطفا یک عکس واضح از چهره‌ات بفرست تا تحلیل شخصیت انجام بدم.\nبرای دریافت تحلیل کامل، عضو VIP شو.")

# دریافت عکس
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    photo = await update.message.photo[-1].get_file()
    path = f"user_{user_id}.jpg"
    await photo.download_to_drive(path)
    await update.message.reply_text("در حال تحلیل چهره شما هستم...")

    try:
        result = DeepFace.analyze(img_path=path, actions=['age', 'gender', 'race', 'emotion'], enforce_detection=False)[0]
        os.remove(path)

        if is_vip(user_id):
            message = f"""✅ تحلیل کامل:
🧠 سن تقریبی: {result['age']}
👤 جنسیت: {result['gender']}
😐 احساس غالب: {result['dominant_emotion']}
🌍 نژاد تخمینی: {result['dominant_race']}
📊 احساسات: {result['emotion']}
"""
        else:
            message = f"""🔍 تحلیل اولیه (رایگان):
😐 احساس غالب: {result['dominant_emotion']}
👤 جنسیت: {result['gender']}
🔓 برای تحلیل کامل و حرفه‌ای، عضو VIP شو: /vip
"""
        await update.message.reply_text(message)

    except Exception as e:
        await update.message.reply_text(f"❌ خطا در تحلیل: {e}")

# دستور VIP کردن (تست دستی)
async def vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    cursor.execute("INSERT OR IGNORE INTO vip_users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    await update.message.reply_text("🎉 شما اکنون عضو VIP هستید. لطفاً دوباره یک عکس بفرست.")

# اجرای ربات
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("vip", vip))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    await app.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
