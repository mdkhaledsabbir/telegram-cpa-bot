import telebot
from telebot import types
import json, os, time

TOKEN = 'আপনার টেলিগ্রাম বট টোকেন'
ADMIN_ID = 8046323012
USER_FILE = 'users.json'
TASK_REWARD = 30
REF_REWARD = 10
MIN_WITHDRAW = 1000
user_screenshot_state = {}

bot = telebot.TeleBot(TOKEN)

if not os.path.exists(USER_FILE):
    with open(USER_FILE, 'w') as f:
        json.dump({}, f)

def load_users():
    with open(USER_FILE, 'r') as f:
        return json.load(f)

def save_users(data):
    with open(USER_FILE, 'w') as f:
        json.dump(data, f)

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    users = load_users()
    ref_id = message.text.split(" ")[-1] if len(message.text.split()) > 1 else None

    if user_id not in users:
        users[user_id] = {"balance": 0, "ref_by": ref_id if ref_id != user_id else None, "refs": []}
        if ref_id and ref_id in users and user_id not in users[ref_id].get("refs", []):
            users[ref_id].setdefault("refs", []).append(user_id)
            users[ref_id]["balance"] += REF_REWARD
        save_users(users)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📋 টাস্ক", "📤 স্ক্রিনশট পাঠান")
    markup.add("💰 ব্যালেন্স", "💸 টাকা উত্তোলন")
    markup.add("👥 রেফারেল লিংক")
    bot.send_message(message.chat.id, "স্বাগতম! নিচের মেনু থেকে কাজ করুন:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "📋 টাস্ক")
def tasks(message):
    task_list = [
        ("Task 1", "Pin submit - https://tinyurl.com/37xxp2an"),
        ("Task 2", "Pin submit - https://tinyurl.com/4vc76fw5"),
        ("Task 3", "Email sub - https://tinyurl.com/yyherfxt"),
        ("Task 4", "Email sub - https://tinyurl.com/25nt96v9")
    ]
    msg = "📝 টাস্কসমূহ:\n"
    for name, link in task_list:
        msg += f"\n🔹 {name}: {link}\n📸 ৩টি স্ক্রিনশট আবশ্যক"
    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda m: m.text == "📤 স্ক্রিনশট পাঠান")
def upload_screenshot(message):
    user_id = message.from_user.id
    user_screenshot_state[user_id] = {"count": 0, "expected": 3}
    bot.send_message(message.chat.id, "📸 এখন ৩টি স্ক্রিনশট পাঠান, একটি একটি করে।")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    if user_id in user_screenshot_state:
        user_screenshot_state[user_id]["count"] += 1
        count = user_screenshot_state[user_id]["count"]
        bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
        bot.send_message(ADMIN_ID, f"🆔 ইউজার: {user_id}\n📸 স্ক্রিনশট {count}/3 জমা দিয়েছে")

        if count >= user_screenshot_state[user_id]["expected"]:
            del user_screenshot_state[user_id]
            bot.send_message(message.chat.id, "✅ ধন্যবাদ! স্ক্রিনশট জমা হয়েছে। এডমিন শীঘ্রই চেক করবেন।")
        else:
            bot.send_message(message.chat.id, f"📸 {count}/3 স্ক্রিনশট পাওয়া গেছে। আরও পাঠান।")
    else:
        bot.send_message(message.chat.id, "❌ আগে '📤 স্ক্রিনশট পাঠান' চাপুন।")

@bot.message_handler(func=lambda m: m.text == "💰 ব্যালেন্স")
def balance(message):
    user_id = str(message.from_user.id)
    users = load_users()
    if user_id in users:
        bal = users[user_id].get("balance", 0)
        refs = len(users[user_id].get("refs", []))
        bot.send_message(message.chat.id, f"💵 ব্যালেন্স: {bal} টাকা\n👥 রেফারেল: {refs} জন")
    else:
        bot.send_message(message.chat.id, "❌ রেজিস্ট্রেশন নেই। /start দিন")

@bot.message_handler(func=lambda m: m.text == "💸 টাকা উত্তোলন")
def withdraw(message):
    user_id = str(message.from_user.id)
    users = load_users()
    balance = users.get(user_id, {}).get("balance", 0)
    if balance < MIN_WITHDRAW:
        bot.send_message(message.chat.id, f"❌ কমপক্ষে {MIN_WITHDRAW} টাকা থাকতে হবে।")
        return
    msg = bot.send_message(message.chat.id, "🧾 bKash/Nagad/Rocket নম্বর দিন:")
    bot.register_next_step_handler(msg, process_withdraw)

def process_withdraw(message):
    user_id = str(message.from_user.id)
    number = message.text.strip()
    users = load_users()
    amount = users[user_id]["balance"]
    users[user_id]["balance"] = 0
    save_users(users)
    bot.send_message(message.chat.id, f"✅ {amount} টাকা উত্তোলনের রিকোয়েস্ট পাঠানো হয়েছে।")
    bot.send_message(ADMIN_ID, f"🔔 নতুন উইথড্র:\n🆔 {user_id}\n💳 নম্বর: {number}\n💰 {amount} টাকা")

@bot.message_handler(func=lambda m: m.text == "👥 রেফারেল লিংক")
def refer(message):
    uid = message.from_user.id
    bot.send_message(message.chat.id, f"🔗 রেফারেল লিংক:\nhttps://t.me/myoffer363bot?start={uid}\nপ্রতি রেফারে {REF_REWARD} টাকা")

# Run Forever
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print("Error:", e)
        time.sleep(5)
