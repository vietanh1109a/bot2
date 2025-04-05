import requests
import time
import logging
import warnings
import html
import re
import json
from concurrent.futures import ThreadPoolExecutor
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

warnings.filterwarnings("ignore", message="Unverified HTTPS request")

# Thông tin bot
TELEGRAM_TOKEN = "7466472123:AAHkvikVLrDjhl3KQVFmDydVzHsfdrdMwRo"
GROUP_CHAT_ID = -1002549023293

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

last_buff_time = {}

# Hàm tăng follow
def buff_follow(username):
    url = f"https://nvp310107.x10.mx/fltik.php?username={username}&key=vphc"
    
    try:
        response = requests.get(url, verify=False)
        data = response.json()

        if data.get("success"):
            user_data = data["data"]
            return f"""
✅ Tăng follow thành công cho: @{username}

📌 Thông Tin Tài Khoản:
🔹 UID: {user_data["user_id"]}
🔹 Nick Name: {user_data["nickname"]}

📊 FOLLOW BAN ĐẦU: {user_data["follower_before"]}
📈 FOLLOW ĐÃ TĂNG: +{user_data["follower_increased"]}
🏆 FOLLOW HIỆN TẠI: {user_data["follower_after"]}
"""
        else:
            message_text = data.get('message', 'Không thể buff follow.')
            wait_time_match = re.search(r'(\d+)\s*giây', message_text)
            if wait_time_match:
                wait_time = wait_time_match.group(1)
                return f"<b>⚠️ Vui Lòng Chờ {wait_time} Giây Trước Khi Thử Lại!</b>\n\nhttps://www.tiktok.com/@{username}"
            return f"⚠️ Lỗi: {message_text}"
    
    except Exception as e:
        return f"⚠️ Lỗi: {e}"

# Hàm kiểm tra xem người dùng có phải admin không
async def is_admin(update: Update) -> bool:
    admins = await update.effective_chat.get_administrators()
    user_id = update.effective_user.id
    return any(admin.user.id == user_id for admin in admins)

# Hàm xử lý lệnh /start
async def start_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    welcome_message = f"""
🎉 Chào mừng bạn đến với VMod!  
🆔 ID của bạn là: <code>{user_id}</code>

🌟 <b>Server có các lệnh như sau:</b>
- <code>/start</code>: Hiển thị thông báo chào mừng và danh sách lệnh 📜
- <code>/fl username</code>: Tăng follow cho tài khoản TikTok (yêu cầu 100 token) 📈
- <code>/buff username</code>: Tăng follow cho tài khoản TikTok <i>(only admin)</i> 🔒
- <code>/addtoken user_id số_token</code>: Thêm token cho một người dùng cụ thể <i>(only admin)</i> 💰
- <code>/checktoken user_id</code>: Kiểm tra số token của một người dùng cụ thể <i>(only admin)</i> 🔍

📩 Nếu cần thêm chức năng gì, ib admin để xem xét!
"""
    await update.message.reply_text(welcome_message, parse_mode="HTML")

# Hàm xử lý lệnh /buff (chỉ admin)
async def buff_command(update: Update, context: CallbackContext):
    global last_buff_time

    if update.effective_chat.id != GROUP_CHAT_ID:
        await update.message.reply_text("❌ Bot chỉ hoạt động trong nhóm được cấp phép.")
        return

    # Kiểm tra quyền admin
    if not await is_admin(update):
        await update.message.reply_text("❌ Chỉ admin mới có thể sử dụng lệnh này!")
        return

    if not context.args:
        await update.message.reply_text("⚠️ Vui lòng nhập username TikTok.\nVí dụ: /buff username_tiktok", parse_mode="Markdown")
        return

    username = context.args[0].strip()

    msg = await update.message.reply_text(f"⏳ Đang tăng follow cho @{username}...")

    with ThreadPoolExecutor(max_workers=1) as executor:
        result = executor.submit(buff_follow, username).result()

    await msg.delete()
    await update.message.reply_text(result, parse_mode="HTML")

    last_buff_time[username] = time.time()

# Cơ sở dữ liệu token
data = {}

def load_data():
    global data
    try:
        with open("tokens.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    return data

def save_data(updated_data):
    global data
    data = updated_data
    with open("tokens.json", "w") as f:
        json.dump(data, f)

# Lệnh /addtoken (chỉ admin, thêm token cho ID được chỉ định)
async def add_token(update: Update, context: CallbackContext):
    if update.effective_chat.id != GROUP_CHAT_ID:
        await update.message.reply_text("❌ Bot chỉ hoạt động trong nhóm được cấp phép.")
        return

    # Kiểm tra quyền admin
    if not await is_admin(update):
        await update.message.reply_text("❌ Chỉ admin mới có thể sử dụng lệnh này!")
        return

    # Kiểm tra tham số: /addtoken <user_id> <token_amount>
    if len(context.args) < 2:
        await update.message.reply_text("⚠️ Vui lòng nhập Telegram ID và số token cần thêm.\nVí dụ: /addtoken 123456789 1000000")
        return

    try:
        target_user_id = str(context.args[0])  # ID của người được thêm token
        token_amount = int(context.args[1])   # Số token cần thêm
        if token_amount <= 0:
            await update.message.reply_text("⚠️ Số token phải lớn hơn 0!")
            return
    except ValueError:
        await update.message.reply_text("⚠️ Telegram ID phải là chuỗi số và số token phải là một số nguyên hợp lệ!")
        return

    data = load_data()

    # Khởi tạo dữ liệu cho user_id nếu chưa có
    if target_user_id not in data:
        data[target_user_id] = {"token": 0}

    # Cấp token cho user_id được chỉ định
    data[target_user_id]["token"] += token_amount
    save_data(data)

    await update.message.reply_text(
        f"✅ Đã cấp thêm {token_amount} token cho ID {target_user_id}! Số token hiện tại: {data[target_user_id]['token']}"
    )

# Lệnh /checktoken (chỉ admin, kiểm tra token của ID được chỉ định)
async def check_token(update: Update, context: CallbackContext):
    if update.effective_chat.id != GROUP_CHAT_ID:
        await update.message.reply_text("❌ Bot chỉ hoạt động trong nhóm được cấp phép.")
        return

    # Kiểm tra quyền admin
    if not await is_admin(update):
        await update.message.reply_text("❌ Chỉ admin mới có thể sử dụng lệnh này!")
        return

    # Kiểm tra tham số: /checktoken <user_id>
    if not context.args:
        await update.message.reply_text("⚠️ Vui lòng nhập Telegram ID cần kiểm tra.\nVí dụ: /checktoken 123456789")
        return

    target_user_id = str(context.args[0])  # ID của người được kiểm tra
    data = load_data()

    # Khởi tạo dữ liệu cho user_id nếu chưa có
    if target_user_id not in data:
        data[target_user_id] = {"token": 0}
        save_data(data)

    await update.message.reply_text(f"💰 Số token hiện tại của ID {target_user_id}: {data[target_user_id]['token']}")

# Hàm xử lý lệnh /fl
async def fl_command(update: Update, context: CallbackContext):
    if update.effective_chat.id != GROUP_CHAT_ID:
        await update.message.reply_text(
            "Tham Gia Nhóm Của Chúng Tôi Để Bot Có Thể Trò Chuyện Với Bạn Dễ Dàng Hơn.\n"
            "Link Đây: [https://t.me/+o8C7qx8oCGlhN2E9]\n\n"
            "Lưu Ý, Bot Chỉ Hoạt Động Trong Những Nhóm Cụ Thể Thôi Nha!"
        )
        return

    data = load_data()
    user_id = str(update.effective_user.id)

    # Khởi tạo dữ liệu người dùng nếu chưa có
    if user_id not in data:
        data[user_id] = {"token": 100}  # Cấp 100 token cho người dùng mới
    
    if data[user_id]["token"] < 100:
        await update.message.reply_text("Bạn không đủ 100 token để sử dụng lệnh này!")
        return

    if not context.args:
        await update.message.reply_text(
            "<b>⚠️ Vui Lòng Nhập Username TikTok</b> \n\nVí dụ: \n<code>/fl bacgau</code>",
            parse_mode="HTML"
        )
        return
    
    username = context.args[0].strip()

    # Lấy thông tin tài khoản từ API
    api2 = f"https://offvn.x10.mx/php/tiktok.php?id={username}"
    try:
        response2 = requests.get(api2, timeout=60, verify=False)
        data_api = response2.json()
    except (requests.RequestException, ValueError):
        await update.message.reply_text("Lỗi Khi Lấy Thông Tin Tài Khoản")
        return
    
    if "data" not in data_api or "user_id" not in data_api["data"]:
        await update.message.reply_text("Không Tìm Thấy Tài Khoản Người Dùng")
        return
    
    info = data_api["data"]

    # Tăng follow
    api1 = f"https://nvp310107.x10.mx/fl.php?username={username}"
    try:
        response1 = requests.get(api1, timeout=60, verify=False)
        if response1.status_code != 200:
            await update.message.reply_text("Lỗi khi tăng follow! API không phản hồi.")
            return
        
        response1_data = response1.json()
        if response1_data.get("success") is False:
            message_text = response1_data.get("message", "")
            wait_time_match = re.search(r'(\d+)\s*giây', message_text)
            if wait_time_match:
                wait_time = wait_time_match.group(1)
                await update.message.reply_text(
                    f"<b>⚠️ Vui Lòng Chờ {wait_time} Giây Trước Khi Thử Lại!</b>\n\nhttps://www.tiktok.com/@{username}",
                    parse_mode="HTML"
                )
                return

    except requests.RequestException:
        await update.message.reply_text("Lỗi Kết Nối Api")
        return
    except ValueError:
        await update.message.reply_text("Lỗi Định Dạng Api")
        return
    
    # Cập nhật token
    data[user_id]["token"] -= 100
    save_data(data)
    remaining_token = data[user_id]["token"]

    # Kết quả
    result = f"""
╭─────────────⭓
│ Tăng Follow Thành Công: @{html.escape(username)}
│ 
│ Nick Name: <code>{html.escape(info.get('nickname', 'N/A'))}</code>
│ UID: <code>{info.get('user_id', 'N/A')}</code>
│ Follower Ban Đầu: <code>{info.get('followers', 'N/A')}</code> Followers
├─────────────⭔
│ TK <a href="tg://user?id={user_id}">{user_id}</a> | GD: <code>-100</code> TOKEN
│ SD: <code>{remaining_token}</code> TOKEN
╰─────────────⭓
"""
    
    await update.message.reply_text(result, parse_mode="HTML")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Thêm các lệnh
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("buff", buff_command))
    app.add_handler(CommandHandler("fl", fl_command))
    app.add_handler(CommandHandler("addtoken", add_token))
    app.add_handler(CommandHandler("checktoken", check_token))

    logging.info("Bot Telegram đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()