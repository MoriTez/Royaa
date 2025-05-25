
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = "@soosssis"

# پیام خوش‌آمدگویی و منوی اصلی
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("ارسال عکس چهره", callback_data="send_photo")],
        [InlineKeyboardButton("طالع‌بینی تولد", callback_data="birth_sign")],
        [InlineKeyboardButton("جفت بودن تاریخ‌ها", callback_data="compatibility")],
        [InlineKeyboardButton("عضویت در کانال", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_text = (
        f"سلام {user.first_name} عزیز!\n\n"
        "من **RoyaBot** هستم. با تحلیل چهره‌ات می‌تونم اطلاعات جالبی از شخصیت، احساسات، ویژگی‌های مخفی و حتی علایق رنگی‌ات بگم!\n"
        "همچنین طالع‌بینی تولدت و سازگاری با دیگران رو هم انجام می‌دم.\n\n"
        "برای شروع یکی از گزینه‌های زیر رو انتخاب کن:"
    )
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

# بررسی کلیک منو
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "send_photo":
        await query.edit_message_text("لطفاً یک عکس واضح از صورت خود ارسال کن تا آنالیز چهره آغاز شود.")
    elif data == "birth_sign":
        await query.edit_message_text("تاریخ تولدت رو به صورت روز/ماه/سال بفرست. مثل: 25/05/1375")
    elif data == "compatibility":
        await query.edit_message_text("دو تاریخ تولد رو به صورت زیر بفرست:\nمثال:\n25/05/1375\n13/11/1373")

# دریافت عکس و بررسی عضویت
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user.id)
    if member.status not in ["member", "creator", "administrator"]:
        keyboard = [[InlineKeyboardButton("عضویت در کانال", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")]]
        markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("برای مشاهده نتیجه کامل، لطفاً اول عضو کانال شو:", reply_markup=markup)
        return

    photo_file = await update.message.photo[-1].get_file()
    os.makedirs("photos", exist_ok=True)
    file_path = f"photos/{user.id}.jpg"
    await photo_file.download_to_drive(file_path)

    await update.message.reply_text("عکس شما با موفقیت دریافت شد. در حال پردازش اولیه...\n(در نسخه بعدی نتیجه تحلیل ظاهر خواهد شد.)")

# ساختار ربات
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(menu_handler))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

if __name__ == "__main__":
    print("ربات در حال اجراست...")
    app.run_polling()
