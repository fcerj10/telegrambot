import telebot
from telebot import types

# 🔹 تنظیمات اصلی
BOT_TOKEN = "8442086787:AAE1_mdqCrd7B438j_QrFYUx_XjSs3fF9WE"
CHANNELS = ["@kirinrealmadrid", "@antimadridgif","@kirinrealmadridtag","@robbermadrid","@kirgoal"]  # لیست کانال‌هایی که باید کاربر عضو باشد
ADMIN_ID = 272920445  # آیدی عددی ادمین

bot = telebot.TeleBot(BOT_TOKEN)

# 🔸 بررسی عضویت کاربر در همه کانال‌ها
def is_member(user_id):
    for ch in CHANNELS:
        try:
            status = bot.get_chat_member(ch, user_id).status
            if status not in ["member", "creator", "administrator"]:
                return False
        except Exception:
            return False
    return True

# 🔹 ساخت دکمه‌های شیشه‌ای برای عضویت
def join_buttons():
    markup = types.InlineKeyboardMarkup()
    for ch in CHANNELS:
        markup.add(types.InlineKeyboardButton(f"📢 عضویت در {ch}", url=f"https://t.me/{ch.replace('@', '')}"))
    markup.add(types.InlineKeyboardButton("✅ بررسی عضویت", callback_data="check"))
    return markup

# 🔹 ساخت دکمه‌های پایانی (بعد از تشکر)
def thank_buttons():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✍️ ارسال سوژه‌ی جدید", callback_data="new"))
    markup.add(types.InlineKeyboardButton("🏠 منوی اصلی", callback_data="menu"))
    return markup

# 🔸 /start
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    if is_member(user_id):
        bot.send_message(
            message.chat.id,
            "✅ خوش اومدی!\nمی‌تونی سوژه‌ت رو بفرستی (متن، عکس یا فایل).\n"
            "سوژه‌هات برای مدیر ارسال می‌شن تا بررسی بشن."
        )
    else:
        bot.send_message(
            message.chat.id,
            "❌ برای ارسال سوژه باید اول عضو کانال‌های زیر بشی 👇",
            reply_markup=join_buttons()
        )

# 🔸 بررسی عضویت از دکمه "بررسی عضویت"
@bot.callback_query_handler(func=lambda call: call.data == "check")
def check_membership(call):
    user_id = call.from_user.id
    if is_member(user_id):
        bot.answer_callback_query(call.id, "✅ عضویت تأیید شد!")
        bot.edit_message_text(
            "✅ عالی! حالا می‌تونی سوژه‌ت رو بفرستی ✍️",
            call.message.chat.id,
            call.message.message_id
        )
    else:
        bot.answer_callback_query(call.id, "❌ هنوز عضو همه کانال‌ها نیستی!")
        bot.edit_message_text(
            "❌ هنوز عضو همه‌ی کانال‌ها نشدی.\n"
            "لطفاً عضو شو و بعد دوباره دکمه بررسی عضویت رو بزن 👇",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=join_buttons()
        )

# 🔸 واکنش به دکمه‌های پایانی (ارسال جدید / منوی اصلی)
@bot.callback_query_handler(func=lambda call: call.data in ["new", "menu"])
def after_thank_buttons(call):
    if call.data == "new":
        bot.answer_callback_query(call.id, "📝 ارسال سوژه جدید")
        bot.send_message(call.message.chat.id, "✍️ لطفاً سوژه‌ت رو بفرست:")
    elif call.data == "menu":
        bot.answer_callback_query(call.id, "🏠 منوی اصلی")
        start(call.message)

# 🔸 دریافت سوژه از کاربران
@bot.message_handler(content_types=["text", "photo", "document"])
def get_submission(message):
    user_id = message.from_user.id

    if not is_member(user_id):
        bot.send_message(
            message.chat.id,
            "❌ برای ارسال سوژه باید اول عضو کانال‌های زیر بشی 👇",
            reply_markup=join_buttons()
        )
        return

    username = f"@{message.from_user.username}" if message.from_user.username else f"ID:{user_id}"
    name = message.from_user.first_name or "بدون‌نام"
    caption = f"📨 سوژه جدید از {name} ({username})"

    # ارسال برای ادمین
    if message.content_type == "text":
        bot.send_message(ADMIN_ID, f"{caption}\n\n📝 {message.text}")
    elif message.content_type == "photo":
        bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=f"{caption}\n\n{message.caption or ''}")
    elif message.content_type == "document":
        bot.send_document(ADMIN_ID, message.document.file_id, caption=f"{caption}\n\n{message.caption or ''}")

# ✅ پیام تشکر با دکمه‌ها
    thank_text = (
        "🙏 ممنون از ارسال سوژه‌ات!\n\n"
        "سوژه‌ات با موفقیت دریافت شد و برای مدیر ارسال شد ✅\n"
        "در صورت مناسب بودن، در کانال منتشر میشه 🌟"
    )
    bot.send_message(message.chat.id, thank_text, reply_markup=thank_buttons())

print("🤖 ربات فعال شد و آماده‌ی کاره...")
bot.infinity_polling()