import telebot
import requests

TOKEN = "7165323948:AAGe59mWIO0IhabXkeXPUyBikXmYcMeaQj4"
bot = telebot.TeleBot(TOKEN)

ALLOWED_GROUP_IDS = [-1002657417803]

@bot.message_handler(commands=['addfr'])
def addfr(message):
    chat_id = message.chat.id
    if chat_id not in ALLOWED_GROUP_IDS:
        return  

    try:
        args = message.text.split()
        if len(args) != 2:
            bot.send_message(chat_id, "⚠️ Vui lòng nhập UID.\nVí dụ: /addfr 12345678", reply_to_message_id=message.message_id)
            return

        uid = args[1]
        url = f"https://spamfriend.vercel.app/addfriend?uid={uid}"
        response = requests.get(url)
        data = response.json()

        if "status" in data and data["status"] == 0:
            bot.send_message(chat_id, "❌ Lỗi. Kiểm tra UID hoặc thử lại sau.", reply_to_message_id=message.message_id)
            return

        nickname = data.get("nickname", "Không rõ")
        level = data.get("level", "Không rõ")
        region = data.get("region", "Không rõ")
        success_count = data.get("success_count", 0)
        sender_name = message.from_user.first_name

        bot.send_message(chat_id,
                         f"<blockquote>🔥 <b>Spam thành công</b> 🔥\n\n"
                         f"- <b>Người Chơi:</b> <code> {nickname}</code>\n"
                         f"- <b>UID:</b> <code>{uid}</code>\n"
                         f"- <b>Khu vực:</b> <code>{region}</code>\n"
                         f"- <b>Cấp độ:</b> <code>{level}</code>\n"
                         f"- <b>Số lượng:</b> <code>{success_count}</code>\n\n"
                         f"<b>☠️Người gửi:</b> {sender_name}</blockquote>", parse_mode="HTML", reply_to_message_id=message.message_id)
    except Exception:
        bot.send_message(chat_id, "❌ Đã xảy ra lỗi. Vui lòng thử lại sau.", reply_to_message_id=message.message_id)

bot.polling()