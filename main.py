import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from dotenv import load_dotenv
from datetime import datetime
import random

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# پیام خوش‌آمدگویی
WELCOME_TEXT = (
    "سلام! به RoyaBot خوش آمدید.\n"
    "من می‌توانم تحلیل چهره، طالع‌بینی، فال حافظ و بررسی فرم بینی انجام دهم.\n"
    "لطفا ابتدا عضو کانال @soosssis شوید تا تحلیل کامل دریافت کنید."
)

# منوی شیشه‌ای
def build_menu():
    keyboard = [
        [InlineKeyboardButton("تحلیل چهره", callback_data='face_analysis')],
        [InlineKeyboardButton("طالع‌بینی تولد", callback_data='birth_analysis')],
        [InlineKeyboardButton("فال حافظ", callback_data='hafez')],
        [InlineKeyboardButton("بررسی فرم بینی", callback_data='nose_shape')],
        [InlineKeyboardButton("وضعیت عضویت در کانال", callback_data='check_membership')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_TEXT, reply_markup=build_menu())

# بررسی عضویت در کانال (تغییر کن به کانال خودت)
CHANNEL_USERNAME = "@soosssis"

async def check_membership(user_id, context):
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logger.error(f"Error checking membership: {e}")
        return False

# تحلیل چهره ساده (نمونه)
def simple_face_analysis():
    analyses = [
        "شخصیت شما مهربان و پرانرژی است.",
        "شما فردی خلاق و باهوش هستید.",
        "چهره شما نشانه اعتماد به نفس بالا است.",
        "نگاه شما پر از احساس و دلسوزی است."
    ]
    return random.choice(analyses)

# طالع‌بینی تولد
def birth_analysis(birthdate_str):
    try:
        birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d')
    except:
        return "فرمت تاریخ تولد صحیح نیست. لطفا به صورت YYYY-MM-DD ارسال کنید."
    month = birthdate.month
    day = birthdate.day
    # مثال ساده طالع‌بینی ماه تولد
    signs = {
        1: "جدی و متعهد",
        2: "خلاق و حساس",
        3: "خوش‌برخورد و اجتماعی",
        4: "قوی و مسئولیت‌پذیر",
        5: "ماجراجو و پرانرژی",
        6: "دوست‌داشتنی و مهربان",
        7: "خودمراقب و درون‌گرا",
        8: "رهبری و جاه‌طلب",
        9: "فیلسوف و منطقی",
        10: "متعادل و صلح‌طلب",
        11: "نوآور و مستقل",
        12: "مردمی و دلسوز"
    }
    return f"طالع‌بینی تولد شما: ماه {month}، شما فردی {signs.get(month, 'خاص')} هستید."

# فال حافظ نمونه (چند بیت)
HAFEZ_POEMS = [
    "الا یا ایها الساقی ادر کاسا و ناولها\nکه عشق آسان نمود اول ولی افتاد مشکل‌ها",
    "دل می‌رود ز دستم صاحب دلان خدا را\nدردا که راز پنهان خواهد شد آشکارا",
    "سرو چمان همی بر نهد سر به سجده ز گل\nچون نرگس به تماشاگه روی تو عیان شود"
]

def get_random_hafez():
    return random.choice(HAFEZ_POEMS)

# بررسی فرم بینی (نمونه)
def nose_shape_analysis():
    shapes = [
        "بینی کشیده نشانگر اعتماد به نفس بالاست.",
        "بینی کوچک نشانه‌ی حساس بودن و دقت زیاد است.",
        "بینی پهن نشان از قدرت تصمیم‌گیری دارد.",
        "بینی سربالا نماد فردی خوش‌برخورد و شاد است."
    ]
    return random.choice(shapes)

# پاسخ به منوی شیشه‌ای
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "face_analysis":
        member = await check_membership(user_id, context)
        if not member:
            await query.edit_message_text("لطفا ابتدا عضو کانال @soosssis شوید تا تحلیل چهره کامل را دریافت کنید.")
            return
        text = simple_face_analysis()
        await query.edit_message_text(f"تحلیل چهره شما:\n\n{text}")

    elif query.data == "birth_analysis":
        await query.edit_message_text("لطفا تاریخ تولد خود را به فرمت YYYY-MM-DD ارسال کنید:")

        context.user_data['expecting_birthdate'] = True

    elif query.data == "hafez":
        poem = get_random_hafez()
        await query.edit_message_text(f"فال حافظ:\n\n{poem}")

    elif query.data == "nose_shape":
        member = await check_membership(user_id, context)
        if not member:
            await query.edit_message_text("برای دیدن تحلیل فرم بینی لطفا عضو کانال @soosssis شوید.")
            return
        analysis = nose_shape_analysis()
        await query.edit_message_text(f"تحلیل فرم بینی شما:\n\n{analysis}")

    elif query.data == "check_membership":
        member = await check_membership(user_id, context)
        if member:
            await query.edit_message_text("شما عضو کانال @soosssis هستید. ممنون از حمایت شما!")
        else:
            await query.edit_message_text("شما عضو کانال @soosssis نیستید. لطفا عضو شوید تا تحلیل‌ها را دریافت کنید.")

# دریافت پیام‌ها (مثل تاریخ تولد)
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('expecting_birthdate'):
        text = update.message.text
        response = birth_analysis(text)
        await update.message.reply_text(response)
        context.user_data['expecting_birthdate'] = False
    else:
        await update.message.reply_text("لطفا از منوی شیشه‌ای برای انتخاب گزینه‌ها استفاده کنید.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message_handler))

    print("ربات در حال اجراست...")
    app.run_polling()

if __name__ == "__main__":
    main()
