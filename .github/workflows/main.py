import telebot
from telebot import types
import json
import os

TOKEN = os.environ.get('TOKEN')
ADMIN_ID = int(os.environ.get('ADMIN_ID'))

bot = telebot.TeleBot(TOKEN)

if not os.path.exists("users.json"):
    with open("users.json", "w") as f:
        json.dump({}, f)

with open("users.json", "r") as f:
    users = json.load(f)

TASKS = {
    "Task 1": "https://tinyurl.com/37xxp2an",
    "Task 2": "https://tinyurl.com/4vc76fw5",
    "Task 3": "https://tinyurl.com/yyherfxt",
    "Task 4": "https://tinyurl.com/25nt96v9"
}

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    ref = message.text.split(" ")[1] if len(message.text.split()) > 1 else None

    if user_id not in users:
        users[user_id] = {"ref_by": ref, "refs": [], "balance": 0}
        if ref and ref != user_id and ref in users:
            users[ref]["refs"].append(user_id)
            users[ref]["balance"] += 10
    save_users()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🧾 টাস্ক", "📤 স্ক্রিনশট দিন", "💰 ব্যালেন্স", "📤 উইথড্র", "👥 রেফার")
    bot.send_message(message.chat.id, "স্বাগতম! নিচের অপশন থেকে নির্বাচন করুন:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🧾 টাস্ক")
def show_tasks(message):
    msg = ""
    for i, (title, link) in enumerate(TASKS.items(), 1):
        msg += f"{i}. {title}: {link}\n"
    msg += "\n👉 প্রতিটি টাস্কের জন্য ৩টি স্ক্রিনশট দিন।"
    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda m: m.text == "💰 ব্যালেন্স")
def balance(message):
    user = users.get(str(message.from_user.id), {})
    bot.send_message(message.chat.id, f"📊 আপনার ব্যালেন্স: {user.get('balance', 0)} টাকা")

@bot.message_handler(func=lambda m: m.text == "📤 উইথড্র")
def withdraw(message):
    user_id = str(message.from_user.id)
    bal = users.get(user_id, {}).get("balance", 0)
    if bal >= 1000:
        bot.send_message(message.chat.id, "✅ আপনার উইথড্র রিকোয়েস্ট গ্রহণ করা হয়েছে, এপ্রুভ হলে জানানো হবে।")
        bot.send_message(ADMIN_ID, f"📤 ইউজার {user_id} উইথড্র চায়, ব্যালেন্স: {bal} টাকা")
    else:
        bot.send_message(message.chat.id, f"❌ উইথড্র করার জন্য অন্তত ১০০০ টাকা থাকতে হবে। আপনার ব্যালেন্স: {bal} টাকা")

@bot.message_handler(func=lambda m: m.text == "👥 রেফার")
def refer(message):
    uid = str(message.from_user.id)
    bot.send_message(message.chat.id, f"🔗 আপনার রেফার লিংক:\nhttps://t.me/myoffer363bot?start={uid}")

@bot.message_handler(func=lambda m: m.text == "📤 স্ক্রিনশট দিন")
def request_screenshot(message):
    bot.send_message(message.chat.id, "🖼️ দয়া করে ৩টি স্ক্রিনশট দিন (একটি একটি করে)।")

@bot.message_handler(content_types=['photo'])
def handle_screenshot(message):
    bot.send_message(message.chat.id, "✅ স্ক্রিনশট গ্রহণ করা হয়েছে, চেক করে এপ্রুভ করা হবে।")
    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)

def save_users():
    with open("users.json", "w") as f:
        json.dump(users, f, indent=2)

print("✅ Bot is running...")
bot.infinity_polling()
