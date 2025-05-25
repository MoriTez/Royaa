import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from dotenv import load_dotenv
from datetime import datetime
import random

# بارگذاری توکن از فایل .env
load_dotenv()
TOKEN = os.getenv("TOKEN")
CHANNEL_USERNAME = "@soosssis"  # نام کانال برای بررسی عضویت

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# منوی شیشه‌ای اولیه
def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("تحلیل چهره", callback_data='face_analysis')],
        [InlineKeyboardButton("تحلیل تولد", callback_data='birth_analysis')],
        [InlineKeyboardButton("فال حافظ", callback_data='hafez')],
        [InlineKeyboardButton("راهنما", callback_data='help')]
    ]
    return InlineKeyboardMarkup(keyboard)

# بررسی عضویت کاربر در کانال
async def is_user_subscribed(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status not in [ChatMember.LEFT, ChatMember.KICKED]
    except:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id

    if not await is_user_subscribed(context, user.id):
        await context.bot.send_message(chat_id, f"سلام {user.first_name}!\nبرای استفاده از این ربات باید ابتدا در کانال ما عضو شوید:\n{CHANNEL_USERNAME}\nبعد /start را دوباره بزنید.")
        return

    await context.bot.send_message(chat_id, f"خوش آمدی {user.first_name}!\nمنوی اصلی:", reply_markup=main_menu_keyboard())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user
    chat_id = query.message.chat_id

    if not await is_user_subscribed(context, user.id):
        await query.edit_message_text(f"برای استفاده از این بخش باید در کانال ما عضو شوید:\n{CHANNEL_USERNAME}")
        return

    data = query.data
    if data == 'face_analysis':
        await query.edit_message_text("لطفا یک عکس سلفی واضح ارسال کنید تا تحلیل چهره انجام شود.")
        context.user_data['waiting_photo'] = True

    elif data == 'birth_analysis':
        await query.edit_message_text("لطفا تاریخ تولد خود را به صورت YYYY-MM-DD ارسال کنید.")
        context.user_data['waiting_birthdate'] = True

    elif data == 'hafez':
        await query.edit_message_text(await get_hafez_fal())

    elif data == 'help':
        help_text = ("راهنما:\n"
                     "1. تحلیل چهره: ارسال عکس برای تحلیل اجزای صورت.\n"
                     "2. تحلیل تولد: ارسال تاریخ تولد برای فال و شخصیت‌شناسی.\n"
                     "3. فال حافظ: دریافت فال حافظ تصادفی.\n"
                     "برای استفاده از همه امکانات باید عضو کانال شوید.")
        await query.edit_message_text(help_text)

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id

    if not await is_user_subscribed(context, user.id):
        await update.message.reply_text(f"برای استفاده از این بخش باید در کانال ما عضو شوید:\n{CHANNEL_USERNAME}")
        return

    if context.user_data.get('waiting_photo', False):
        photo_file = await update.message.photo[-1].get_file()
        photo_path = f"photos/{user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        await photo_file.download_to_drive(photo_path)

        await update.message.reply_text("عکس شما با موفقیت دریافت شد. در حال پردازش...")
        result = await analyze_face(photo_path)
        await update.message.reply_text(result)

        context.user_data['waiting_photo'] = False
    else:
        await update.message.reply_text("برای شروع تحلیل چهره، از منوی اصلی گزینه 'تحلیل چهره' را انتخاب کنید.")

async def birthdate_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id

    if not await is_user_subscribed(context, user.id):
        await update.message.reply_text(f"برای استفاده از این بخش باید در کانال ما عضو شوید:\n{CHANNEL_USERNAME}")
        return

    if context.user_data.get('waiting_birthdate', False):
        text = update.message.text.strip()
        try:
            birthdate = datetime.strptime(text, "%Y-%m-%d")
            result = analyze_birthdate(birthdate)
            await update.message.reply_text(result)
        except:
            await update.message.reply_text("فرمت تاریخ صحیح نیست. لطفا به شکل YYYY-MM-DD ارسال کنید.")
        context.user_data['waiting_birthdate'] = False
    else:
        await update.message.reply_text("برای شروع تحلیل تولد، از منوی اصلی گزینه 'تحلیل تولد' را انتخاب کنید.")

async def analyze_face(photo_path: str) -> str:
    # این قسمت باید با الگوریتم‌های واقعی تشخیص چهره، لب، بینی، رنگ چشم، خال و ... جایگزین شود
    # اینجا برای نمونه فقط یک متن تست میده
    return ("تحلیل چهره:\n"
            "- لب‌ها: طبیعی و متعادل\n"
            "- بینی: دارای قوس مناسب\n"
            "- رنگ چشم: قهوه‌ای روشن\n"
            "- خال: چند خال کوچک و ظریف\n"
            "\n"
            "بر اساس چهره شما، فردی با اعتماد به نفس و آرام هستید.")

def analyze_birthdate(birthdate: datetime) -> str:
    # مثال تحلیل تولد ساده بر اساس ماه تولد
    month = birthdate.month
    descriptions = {
        1: "شما فردی مصمم و با اراده هستید.",
        2: "شما فردی خلاق و مهربان هستید.",
        3: "شما فردی باهوش و حساس هستید.",
        4: "شما فردی با انگیزه و پر انرژی هستید.",
        5: "شما فردی صبور و دل‌نشین هستید.",
        6: "شما فردی متفکر و آرام هستید.",
        7: "شما فردی شجاع و پر احساس هستید.",
        8: "شما فردی هدفمند و منظم هستید.",
        9: "شما فردی مهربان و خلاق هستید.",
        10: "شما فردی اجتماعی و با محبت هستید.",
        11: "شما فردی با هوش بالا و زیرک هستید.",
        12: "شما فردی صبور و مسئولیت‌پذیر هستید."
    }
    return f"تحلیل تولد شما:\n{descriptions.get(month, 'اطلاعات کافی نیست')}"

async def get_hafez_fal() -> str:
    # چند بیت نمونه از فال حافظ (می‌تونی بیشترش کنی)
    fal_list = [
        "دل به دل راه دارد.",
        "یک گل بهار نمی‌آورد.",
        "بر دل هر که مهر دوست دارد، چراغ محبت افروزد.",
        "حافظا! از کرم تو حاجت روا شد."
    ]
    return f"فال حافظ:\n{random.choice(fal_list)}"

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), birthdate_handler))

    print("ربات در حال اجراست...")
    app.run_polling()

if __name__ == '__main__':
    main()
