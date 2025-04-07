import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import requests
import json
import re
import datetime
# Cấu hình logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Bot Token 
TOKEN = "8061781080:AAGmr62iGl_cUjLrdxzAPpxiV4ZB-Rxqt5o"

# API URL
TIKTOK_API_URL = "https://hoangkhiemtruong.cameraddns.net/tiktok/info.php?username="
TIKTOK_VIDEO_API_URL = "https://hoangkhiemtruong.cameraddns.net/tiktok/video.php?url="
TIKTOK_FOLLOW_API_URL = "https://hoangkhiemtruong.cameraddns.net/hoangkhiem/follow.php?username="
FREEFIRE_OUTFIT_API_URL = "https://marcoxirotech-outfit.vercel.app/api?region=vn&uid="
FREEFIRE_API_KEY = "MARCOxIROTECH"
# Thêm hằng số này ở đầu file cùng với các hằng số khác
ALLOWED_GROUP_ID = -1002549023293  # Thay bằng ID nhóm thực tế của bạn

# Tạo hàm kiểm tra xem tin nhắn có đến từ nhóm được phép không
async def check_authorized_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kiểm tra xem lệnh có đến từ nhóm được phép không"""
    chat_id = update.effective_chat.id
    
    if chat_id != ALLOWED_GROUP_ID:
        await update.message.reply_text("⚠️ Bot này chỉ hoạt động trong nhóm được chỉ định. 🔒\n Nhóm tele: t.me/vmod123z")
        return False
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gửi tin nhắn khi lệnh /start được dùng."""
    if not await check_authorized_group(update, context):
        return
    
    await update.message.reply_text(
        '🤖 Chào Mừng đến với VMOD bot!!!\n\n'

        '📋 Sử dụng các lệnh sau:\n\n'

        '📊 /infotiktok:  Lấy thông tin tài khoản TikTok\n'
        '🎬 /videotiktok:  Lấy thông tin video TikTok\n'
        '👥 /fl:  Tăng follow cho tài khoản TikTok\n'
        '👗 /tpff:  Lấy ảnh trang phục Free Fire\n'
        '👁️ /viewff:  Tăng lượt xem cho tài khoản Free Fire\n'
        '📱 /fb:  Lấy thông tin tài khoản Facebook\n'
        '🎮 /infoff:  Lấy thông tin tài khoản Free Fire\n'
        '🤝 /addfr:  Spam kết bạn Free Fire'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gửi tin nhắn khi lệnh /help được dùng."""
    if not await check_authorized_group(update, context):
        return
    await update.message.reply_text(
        'Sử dụng các lệnh sau:\n\n'
        '1. Lấy thông tin tài khoản TikTok:\n'
        '/infotiktok @username hoặc /infotiktok username\n'
        'Ví dụ: /infotiktok vietlegendc\n\n'
        '2. Lấy thông tin video TikTok:\n'
        '/videotiktok URL\n'
        'Ví dụ: /videotiktok https://www.tiktok.com/@bomaydeptraibomaycoquyen/video/7483809457726704914\n\n'
        '3. Tăng follow cho tài khoản TikTok:\n'
        '/fl username\n'
        'Ví dụ: /fl vietlegendc\n\n'
        '4. Lấy ảnh trang phục Free Fire:\n'
        '/tpff uid\n'
        'Ví dụ: /tpff 833822096\n\n'
        '5. Tăng lượt xem cho tài khoản Free Fire:\n'
        '/viewff uid\n'
        'Ví dụ: /viewff 833822096\n\n'
        '6. Lấy thông tin tài khoản Facebook:\n'
        '/fb link\n'
        'Ví dụ: /fb https://www.facebook.com/VietLegendc\n'
        '7. Check thông tin tài khoản Free Fire:\n'
        '/infoff uid\n'
        'Ví dụ: /infoff 833822096\n\n'
        '8. Spam kết bạn Free Fire:\n'
        '/addfr uid\n'
        'ví dụ /addfr 833822096\n\n'
    )

async def get_tiktok_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lấy và hiển thị thông tin người dùng TikTok."""
    if not await check_authorized_group(update, context):
        return
    try:
        # Lấy username từ tin nhắn
        if not context.args:
            await update.message.reply_text("Vui lòng cung cấp username TikTok. Ví dụ: /infotiktok vietlegendc")
            return

        # Lấy username và xóa @ nếu có
        username = context.args[0].replace('@', '')
        
        # Thông báo đang xử lý
        processing_msg = await update.message.reply_text(f"Đang lấy thông tin cho {username}...")
        
        # Gửi request đến API
        response = requests.get(f"{TIKTOK_API_URL}{username}")
        
        # Kiểm tra response
        if response.status_code != 200:
            await update.message.reply_text(f"Lỗi: Không thể kết nối đến API. Mã lỗi: {response.status_code}")
            await processing_msg.delete()
            return
        
        # Parse JSON
        try:
            data = response.json()
        except json.JSONDecodeError:
            await update.message.reply_text("Lỗi: API trả về dữ liệu không hợp lệ")
            await processing_msg.delete()
            return
        
        # Kiểm tra nếu data không phải là dictionary
        if not isinstance(data, dict):
            await update.message.reply_text("Lỗi: API trả về dữ liệu không đúng định dạng")
            await processing_msg.delete()
            return
        
        # Kiểm tra nếu request thành công
        if data.get("code") != 0:
            error_msg = data.get('msg', 'Không tìm thấy thông tin')
            
            # Kiểm tra lỗi Free API Limit
            if "Free Api Limit" in error_msg:
                await update.message.reply_text("Vui lòng nhập đúng lệnh và thử lại sau ít giây.")
            else:
                # Kiểm tra lỗi sai định dạng username
                if "User not found" in error_msg or "user not exist" in error_msg:
                    await update.message.reply_text(f"Lỗi: Username '{username}' không tồn tại. Vui lòng kiểm tra lại và nhập đúng định dạng username TikTok.")
                else:
                    await update.message.reply_text(f"Lỗi: {error_msg}")
            
            await processing_msg.delete()
            return
        
        # Lấy thông tin người dùng
        user_data = data.get("data", {}).get("user", {})
        stats_data = data.get("data", {}).get("stats", {})
        
        # Đảm bảo user_data và stats_data là dictionary
        if not isinstance(user_data, dict):
            user_data = {}
        if not isinstance(stats_data, dict):
            stats_data = {}
        
        # Tạo tin nhắn thông tin cơ bản
        info_message = (
            f"📊 THÔNG TIN TIKTOK 📊\n\n"
            f"👤 Nickname: {user_data.get('nickname', 'N/A')}\n"
            f"🆔 ID: {user_data.get('id', 'N/A')}\n"
            f"👨‍💻 Username: @{user_data.get('uniqueId', 'N/A')}\n"
            f"📝 Tiểu sử: {user_data.get('signature', 'Không có tiểu sử')}\n"
            f"✅ Đã xác minh: {'Có' if user_data.get('verified') else 'Không'}\n"
            f"🔒 Tài khoản riêng tư: {'Có' if user_data.get('privateAccount') else 'Không'}\n"
        )
        
        # Thêm thông tin về tài khoản mạng xã hội liên kết
        social_message = (
            f"\n🔗 MẠNG XÃ HỘI LIÊN KẾT 🔗\n"
            f"📸 Instagram: {user_data.get('ins_id') if user_data.get('ins_id') else 'Không liên kết'}\n"
            f"🐦 Twitter: {user_data.get('twitter_id') if user_data.get('twitter_id') else 'Không liên kết'}\n"
        )
        
        # Thêm thông tin về kênh YouTube nếu có
        youtube_message = ""
        if user_data.get('youtube_channel_id') or user_data.get('youtube_channel_title'):
            youtube_message = (
                f"📺 YouTube: {user_data.get('youtube_channel_title', 'Không có tên')}\n"
                f"📺 ID YouTube: {user_data.get('youtube_channel_id', 'Không có ID')}\n"
            )
        
        # Thêm thông tin thống kê
        stats_message = (
            f"\n📈 THỐNG KÊ 📈\n"
            f"👥 Đang theo dõi: {stats_data.get('followingCount', 0):,}\n"
            f"👥 Người theo dõi: {stats_data.get('followerCount', 0):,}\n"
            f"❤️ Tổng lượt thích: {stats_data.get('heartCount', 0):,}\n"
            f"🎬 Số video: {stats_data.get('videoCount', 0):,}\n"
            f"👍 Lượt thích: {stats_data.get('diggCount', 0):,}\n"
        )
        
        # Kết hợp tất cả thông tin
        full_message = info_message + social_message + youtube_message + stats_message
        
        # Thêm thông tin về thời gian xử lý API
        full_message += f"\n⏱️ Thời gian xử lý: {data.get('processed_time', 'N/A')} giây"
        
        # Nếu có avatar, gửi ảnh kèm theo text
        avatar_url = user_data.get('avatarLarger')
        if avatar_url:
            # Kiểm tra độ dài caption, nếu quá dài thì chia nhỏ tin nhắn
            if len(full_message) > 1024:  # Telegram giới hạn caption tối đa 1024 ký tự
                await update.message.reply_photo(
                    photo=avatar_url,
                    caption=info_message[:1024]  # Gửi phần đầu với ảnh
                )
                # Gửi phần còn lại là text riêng
                remaining_message = social_message + youtube_message + stats_message
                await update.message.reply_text(remaining_message)
            else:
                await update.message.reply_photo(
                    photo=avatar_url,
                    caption=full_message
                )
        else:
            # Nếu không có avatar, gửi toàn bộ dưới dạng text
            await update.message.reply_text(full_message)
        
        # Xóa tin nhắn đang xử lý
        await processing_msg.delete()
        
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        await update.message.reply_text(f"Đã xảy ra lỗi: {str(e)}")
        if processing_msg:
            await processing_msg.delete()

async def get_tiktok_video_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lấy và hiển thị thông tin video TikTok."""
    if not await check_authorized_group(update, context):
        return
    try:
        # Lấy URL từ tin nhắn
        if not context.args:
            await update.message.reply_text("Vui lòng cung cấp URL video TikTok.\n Ví dụ: /videotiktok https://www.tiktok.com/@bomaydeptraibomaycoquyen/video/7483809457726704914")
            return

        # Lấy URL video
        video_url = context.args[0]
        
        # Kiểm tra URL có đúng định dạng TikTok không
        if not re.search(r'(tiktok\.com|douyin\.com)', video_url):
            await update.message.reply_text("URL không hợp lệ. Vui lòng cung cấp URL TikTok hợp lệ.")
            return
        
        # Thông báo đang xử lý
        processing_msg = await update.message.reply_text("Đang lấy thông tin video...")
        
        # Gửi request đến API
        response = requests.get(f"{TIKTOK_VIDEO_API_URL}{video_url}")
        
        # Kiểm tra response
        if response.status_code != 200:
            await update.message.reply_text(f"Lỗi: Không thể kết nối đến API. Mã lỗi: {response.status_code}")
            await processing_msg.delete()
            return
        
        # Parse JSON và log response để debug
        try:
            data = response.json()
            logging.info(f"API Response: {json.dumps(data, indent=2)}")
        except json.JSONDecodeError:
            await update.message.reply_text("Lỗi: API trả về dữ liệu không hợp lệ")
            await processing_msg.delete()
            return
        
        # Kiểm tra nếu request thành công
        if data.get("code") != 0:
            await update.message.reply_text(f"Lỗi: {data.get('msg', 'Không tìm thấy thông tin')}")
            await processing_msg.delete()
            return
        
        # Lấy thông tin video theo cấu trúc API mới
        video_data = data.get("data", {})
        
        # Kiểm tra xem data có cấu trúc mới không
        if "region" in video_data:
            # Xử lý theo cấu trúc mới
            region = video_data.get("region", "N/A")
            title = video_data.get("title", "Không có mô tả")
            duration = video_data.get("duration", 0)
            play_url = video_data.get("play", "")
            cover_url = ""
            
            # Lấy cover URL từ các định dạng khác nhau
            cover_data = video_data.get("cover", {})
            if isinstance(cover_data, dict):
                # Ưu tiên format lớn nhất nếu có
                cover_formats = ["origin", "default", "r540"]
                for format in cover_formats:
                    if format in cover_data and cover_data[format]:
                        cover_url = cover_data[format]
                        break
            elif isinstance(cover_data, str):
                cover_url = cover_data
                
            # Lấy thông tin âm nhạc
            music_info = video_data.get("music_info", {})
            music_title = "N/A"
            music_author = "N/A"
            
            if isinstance(music_info, dict):
                music_title = music_info.get("title", "N/A")
                music_author = music_info.get("author", "N/A")
            
            # Lấy thông tin thống kê
            play_count = video_data.get("play_count", 0)
            digg_count = video_data.get("digg_count", 0)
            comment_count = video_data.get("comment_count", 0)
            share_count = video_data.get("share_count", 0)
            collect_count = video_data.get("collect_count", 0)
            
            # Lấy thông tin tác giả
            author_data = video_data.get("author", {})
            author_id = "N/A"
            author_name = "N/A"
            author_username = "N/A"
            
            if isinstance(author_data, dict):
                author_id = author_data.get("id", "N/A")
                author_name = author_data.get("nickname", "N/A")
                author_username = author_data.get("unique_id", "N/A")
            
            # Tạo tin nhắn thông tin video
            video_info = (
                f"🎬 THÔNG TIN VIDEO TIKTOK 🎬\n\n"
                f"📝 Tiêu đề: {title}\n"
                f"⏱️ Thời lượng: {duration} giây\n"
                f"🌍 Khu vực: {region}\n"
            )
            
            # Thông tin tác giả
            author_info = (
                f"\n👤 THÔNG TIN TÁC GIẢ 👤\n"
                f"📛 Nickname: {author_name}\n"
                f"🆔 ID: {author_id}\n"
                f"👨‍💻 Username: @{author_username}\n"
            )
            
            # Thông tin về nhạc
            music_info_text = (
                f"\n🎵 THÔNG TIN NHẠC 🎵\n"
                f"🎵 Tên bài hát: {music_title}\n"
                f"👤 Tác giả: {music_author}\n"
            )
            
            # Thông tin thống kê
            stats_info = (
                f"\n📊 THỐNG KÊ 📊\n"
                f"❤️ Lượt thích: {digg_count:,}\n"
                f"💬 Bình luận: {comment_count:,}\n"
                f"🔄 Chia sẻ: {share_count:,}\n"
                f"👁️ Lượt xem: {play_count:,}\n"
                f"📥 Đã lưu: {collect_count:,}\n"
            )
        else:
            # Xử lý theo cấu trúc cũ
            # Đảm bảo video_data là dictionary
            if not isinstance(video_data, dict):
                video_data = {}
                
            author_data = video_data.get("author", {})
            music_data = video_data.get("music", {})
            stats_data = video_data.get("stats", {})
            
            # Đảm bảo các dictionary con đều hợp lệ
            if not isinstance(author_data, dict):
                author_data = {}
            if not isinstance(music_data, dict):
                music_data = {}
            if not isinstance(stats_data, dict):
                stats_data = {}
            
            # Xử lý thông tin video
            title = video_data.get("desc", "Không có mô tả")
            
            # Đảm bảo video object là dictionary
            video_obj = video_data.get("video", {})
            if not isinstance(video_obj, dict):
                video_obj = {}
                
            play_url = video_obj.get("downloadAddr", "")
            cover_url = video_obj.get("cover", "")
            dynamic_cover = video_obj.get("dynamicCover", "")
            duration = video_obj.get("duration", 0)
            
            if dynamic_cover:
                cover_url = dynamic_cover
            
            # Tạo tin nhắn thông tin video
            video_info = (
                f"🎬 THÔNG TIN VIDEO TIKTOK 🎬\n\n"
                f"📝 Mô tả: {title}\n"
                f"⏱️ Thời lượng: {duration} giây\n"
            )
            
            # Thông tin tác giả
            author_info = (
                f"\n👤 THÔNG TIN TÁC GIẢ 👤\n"
                f"📛 Nickname: {author_data.get('nickname', 'N/A')}\n"
                f"🆔 ID: {author_data.get('id', 'N/A')}\n"
                f"👨‍💻 Username: @{author_data.get('uniqueId', 'N/A')}\n"
                f"✅ Đã xác minh: {'Có' if author_data.get('verified') else 'Không'}\n"
            )
            
            # Thông tin về nhạc
            music_info_text = (
                f"\n🎵 THÔNG TIN NHẠC 🎵\n"
                f"🎵 Tên bài hát: {music_data.get('title', 'N/A')}\n"
                f"👤 Tác giả: {music_data.get('authorName', 'N/A')}\n"
                f"⏱️ Thời lượng: {music_data.get('duration', 0)} giây\n"
            )
            
            # Thông tin thống kê
            stats_info = (
                f"\n📊 THỐNG KÊ 📊\n"
                f"❤️ Lượt thích: {stats_data.get('diggCount', 0):,}\n"
                f"💬 Bình luận: {stats_data.get('commentCount', 0):,}\n"
                f"🔄 Chia sẻ: {stats_data.get('shareCount', 0):,}\n"
                f"👁️ Lượt xem: {stats_data.get('playCount', 0):,}\n"
                f"📥 Đã lưu: {stats_data.get('collectCount', 0):,}\n"
            )
        
        # Kết hợp tất cả thông tin
        full_message = video_info + author_info + music_info_text + stats_info
        
        # Thêm thông tin về thời gian xử lý API
        full_message += f"\n⏱️ Thời gian xử lý: {data.get('processed_time', 'N/A')} giây"
        
        # Nếu có cover, gửi ảnh kèm theo text
        if cover_url:
            # Kiểm tra độ dài caption, nếu quá dài thì chia nhỏ tin nhắn
            if len(full_message) > 1024:  # Telegram giới hạn caption tối đa 1024 ký tự
                await update.message.reply_photo(
                    photo=cover_url,
                    caption=video_info[:1024]  # Gửi phần đầu với ảnh
                )
                # Gửi phần còn lại là text riêng
                remaining_message = author_info + music_info_text + stats_info
                await update.message.reply_text(remaining_message)
            else:
                await update.message.reply_photo(
                    photo=cover_url,
                    caption=full_message
                )
        else:
            # Nếu không có avatar, gửi toàn bộ dưới dạng text
            await update.message.reply_text(full_message)
        
        # Nếu có URL video, gửi nút để tải về - ĐÃ CẬP NHẬT SỬ DỤNG HTML HYPERLINK
        if play_url:
            await update.message.reply_text(
                f"📥 Link tải video: <a href=\"{play_url}\">bấm vào đây</a>\n\n"
                f"👉 Bạn có thể tải trực tiếp video từ link trên.",
                parse_mode="HTML"
            )
        
        # Xóa tin nhắn đang xử lý
        await processing_msg.delete()
        
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        await update.message.reply_text(f"Đã xảy ra lỗi: {str(e)}")

async def increase_tiktok_followers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Tăng follow cho tài khoản TikTok."""
    if not await check_authorized_group(update, context):
        return
    try:
        # Lấy username từ tin nhắn
        if not context.args:
            await update.message.reply_text("Vui lòng cung cấp username TikTok. Ví dụ: /fl vietlegendc")
            return

        # Lấy username và xóa @ nếu có
        username = context.args[0].replace('@', '')
        
        # Thông báo đang xử lý
        processing_msg = await update.message.reply_text(f"Đang tăng follow cho {username}...")
        
        # Gửi request đến API
        response = requests.get(f"{TIKTOK_FOLLOW_API_URL}{username}")
        
        # Kiểm tra response
        if response.status_code != 200:
            await update.message.reply_text(f"Lỗi: Không thể kết nối đến API. Mã lỗi: {response.status_code}")
            await processing_msg.delete()
            return
        
        # Parse JSON
        try:
            data = response.json()
            logging.info(f"Follow API Response: {json.dumps(data, indent=2)}")
        except json.JSONDecodeError:
            await update.message.reply_text("Lỗi: API trả về dữ liệu không hợp lệ")
            await processing_msg.delete()
            return
        
        # Kiểm tra status "wait"
        if "status" in data and data["status"] == "wait":
            wait_message = data.get("message", "Vui lòng đợi một khoảng thời gian trước khi thử lại.")
            owner_info = data.get("owner", "")
            
            # Tạo thông báo chờ đợi
            wait_response = (
                f"⏳ YÊU CẦU CẦN CHỜ ⏳\n\n"
                f"👤 Username: @{username}\n"
                f"📝 Thông báo: {wait_message}\n"
            )
            
            # Thêm thông tin về chủ sở hữu nếu có
            if owner_info:
                wait_response += f"👨‍💻 Liên hệ: @vietanhzzz\n"
                
            await update.message.reply_text(wait_response)
            await processing_msg.delete()
            return
            
        # Kiểm tra response từ API và tạo thông báo phù hợp
        if "code" in data:
            # Nếu API trả về code
            if data.get("code") == 0 or data.get("code") == 200:
                # Thành công
                success_message = (
                    f"✅ TĂNG FOLLOW THÀNH CÔNG ✅\n\n"
                    f"👤 Username: @{username}\n"
                )
                
                # Thêm thông tin số lượng follow đã tăng nếu có
                if "data" in data and "follower_count" in data["data"]:
                    success_message += f"👥 Số follow đã tăng: {data['data']['follower_count']:,}\n"
                
                # Thêm thông tin thời gian xử lý nếu có
                if "processed_time" in data:
                    success_message += f"⏱️ Thời gian xử lý: {data['processed_time']} giây\n"
                
                await update.message.reply_text(success_message)
            else:
                # Thất bại với mã lỗi
                error_msg = data.get("msg", "Không rõ lỗi")
                await update.message.reply_text(f"❌ Lỗi: {error_msg}")
        elif "success" in data:
            # Nếu API trả về success
            if data.get("success") == True:
                success_message = (
                    f"✅ TĂNG FOLLOW THÀNH CÔNG ✅\n\n"
                    f"👤 Username: @{username}\n"
                )
                
                # Thêm thông tin từ response nếu có
                if "message" in data:
                    success_message += f"📝 Thông báo: {data['message']}\n"
                
                # Thêm thông tin số lượng follow nếu có
                if "data" in data and isinstance(data["data"], dict):
                    if "follower_count" in data["data"]:
                        success_message += f"👥 Số follow đã tăng: {data['data']['follower_count']:,}\n"
                
                await update.message.reply_text(success_message)
            else:
                # Thất bại
                error_msg = data.get("message", "Không thể tăng follow")
                await update.message.reply_text(f"❌ Lỗi: {error_msg}")
        else:
            # Không có mẫu response tiêu chuẩn, trả về thông báo chung
            await update.message.reply_text(
                f"✅ Đã gửi yêu cầu tăng follow cho @{username}\n\n"
                f"👉 Vui lòng kiểm tra tài khoản TikTok sau vài phút để xem kết quả."
            )
        
        # Xóa tin nhắn đang xử lý
        await processing_msg.delete()
        
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        await update.message.reply_text(f"Đã xảy ra lỗi: {str(e)}")

async def get_freefire_outfit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lấy và hiển thị ảnh trang phục Free Fire."""
    if not await check_authorized_group(update, context):
        return
    try:
        # Lấy UID từ tin nhắn
        if not context.args:
            await update.message.reply_text("Vui lòng cung cấp UID Free Fire. Ví dụ: /tpff 833822096")
            return

        # Lấy UID
        uid = context.args[0]
        
        # Kiểm tra UID có phải là số không
        if not uid.isdigit():
            await update.message.reply_text("UID không hợp lệ. UID phải là một dãy số.")
            return
        
        # Thông báo đang xử lý
        processing_msg = await update.message.reply_text(f"Đang lấy thông tin trang phục Free Fire cho UID {uid}...")
        
        # Tạo URL API với region mặc định là "vn"
        api_url = f"{FREEFIRE_OUTFIT_API_URL}{uid}&key={FREEFIRE_API_KEY}"
        
        logging.info(f"Requesting Free Fire outfit API: {api_url}")
        
        # Gửi request đến API
        response = requests.get(api_url)
        
        # Kiểm tra response
        if response.status_code != 200:
            await update.message.reply_text(f"Lỗi: Không thể kết nối đến API. Mã lỗi: {response.status_code}")
            await processing_msg.delete()
            return
        
        # Kiểm tra content type
        content_type = response.headers.get('Content-Type', '')

        # Kiểm tra xem response có phải là hình ảnh hay không
        if 'image' in content_type:
            # Nếu là hình ảnh, gửi trực tiếp
            await update.message.reply_photo(
                photo=response.content,
                caption=f"🎮 TRANG PHỤC FREE FIRE 🎮\n\n👤 UID: {uid}\n🌍 Region: vn"
            )
        else:
            # Nếu không phải hình ảnh, thử parse dưới dạng JSON
            try:
                data = response.json()
                logging.info(f"Free Fire API Response: {json.dumps(data, indent=2)}")
                
                # Kiểm tra lỗi
                if data.get("error"):
                    await update.message.reply_text(f"❌ Lỗi: {data.get('message', 'Không tìm thấy thông tin')}")
                elif data.get("url"):
                    # Nếu có URL hình ảnh, gửi hình ảnh
                    await update.message.reply_photo(
                        photo=data.get("url"),
                        caption=f"🎮 TRANG PHỤC FREE FIRE 🎮\n\n👤 UID: {uid}\n🌍 Region: vn\n👤 Nickname: {data.get('nickname', 'N/A')}"
                    )
                else:
                    await update.message.reply_text("Không thể lấy thông tin trang phục.")
            except json.JSONDecodeError:
                await update.message.reply_text("API trả về dữ liệu không đúng định dạng.")

        # Xóa tin nhắn đang xử lý
        await processing_msg.delete()
        
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        await update.message.reply_text(f"Đã xảy ra lỗi: {str(e)}")
async def get_facebook_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lấy và hiển thị thông tin tài khoản Facebook."""
    if not await check_authorized_group(update, context):
        return
    try:
        # Lấy link từ tin nhắn
        if not context.args:
            await update.message.reply_text("Vui lòng cung cấp link Facebook.\n Ví dụ: /fb https://www.facebook.com/VietLegendc")
            return

        # Lấy link Facebook
        facebook_link = context.args[0]
        
        # Kiểm tra link có chứa facebook không
        if not re.search(r'facebook\.com', facebook_link):
            await update.message.reply_text("Link không hợp lệ. Vui lòng cung cấp link Facebook hợp lệ.")
            return
        
        # Thông báo đang xử lý
        processing_msg = await update.message.reply_text("Đang lấy thông tin Facebook...")
        
        # Gửi request đến API
        api_url = f"https://api.ffcommunity.site/getID.php?linkFB={facebook_link}"
        response = requests.get(api_url)
        
        # Kiểm tra response
        if response.status_code != 200:
            await update.message.reply_text(f"Lỗi: Không thể kết nối đến API. Mã lỗi: {response.status_code}")
            await processing_msg.delete()
            return
        
        # Parse JSON
        try:
            data = response.json()
        except json.JSONDecodeError:
            await update.message.reply_text("Lỗi: API trả về dữ liệu không hợp lệ")
            await processing_msg.delete()
            return
        
        # Kiểm tra nếu request thành công
        if data.get("error") != 0:
            await update.message.reply_text(f"Lỗi: {data.get('msg', 'Không tìm thấy thông tin')}")
            await processing_msg.delete()
            return
        
        # Tạo tin nhắn thông tin Facebook
        info_message = (
            f"✅ THÔNG TIN FACEBOOK ✅\n\n"
            f"🆔 ID: {data.get('id', 'N/A')}\n"
            f"👤 Tên: {data.get('name', 'N/A')}\n"
            f"🔗 Link: {facebook_link}"
        )
        
        # Gửi thông tin
        await update.message.reply_text(info_message)
        
        # Xóa tin nhắn đang xử lý
        await processing_msg.delete()
        
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        await update.message.reply_text(f"Đã xảy ra lỗi: {str(e)}")
async def get_freefire_views(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Tăng lượt xem cho tài khoản Free Fire."""
    if not await check_authorized_group(update, context):
        return
    try:
        # Lấy UID từ tin nhắn
        if not context.args:
            await update.message.reply_text("Vui lòng cung cấp UID Free Fire. Ví dụ: /viewff 833822096")
            return

        # Lấy UID
        uid = context.args[0]
        
        # Kiểm tra UID có phải là số không
        if not uid.isdigit():
            await update.message.reply_text("UID không hợp lệ. UID phải là một dãy số.")
            return
        
        # Thông báo đang xử lý
        processing_msg = await update.message.reply_text(f"Đang gửi lượt xem cho UID Free Fire {uid}...")
        
        # Tạo URL API với region mặc định là "vn"
        api_url = f"https://visits-lk-tm-v2.vercel.app/{uid}"
        
        logging.info(f"Requesting Free Fire view API: {api_url}")
        
        # Gửi request đến API
        response = requests.get(api_url)
        
        # Kiểm tra response
        if response.status_code != 200:
            await update.message.reply_text(f"Lỗi: Không thể kết nối đến API. Mã lỗi: {response.status_code}")
            await processing_msg.delete()
            return
        
        # Parse JSON
        try:
            data = response.json()
            logging.info(f"Free Fire View API Response: {json.dumps(data, indent=2)}")
            
            # Tạo tin nhắn thành công
            success_message = (
                f"✅ TĂNG VIEW FREE FIRE THÀNH CÔNG ✅\n\n"
                f"👤 UID: {uid}\n"
                f"🌍 Region: vn\n"
            )
            
            # Thêm thông báo từ API nếu có
            if "message" in data:
                success_message += f"📝 Thông báo: {data.get('message')}\n"
            
            # Thêm thông tin nhóm nếu có
            if "group" in data:
                success_message += f"👥 Nhóm: t.me/vmod123z\n"
            
            # Thêm thông tin liên hệ chủ sở hữu
            success_message += f"👨‍💻 Liên hệ: @vietanhzzz\n"
            
            await update.message.reply_text(success_message)
            
        except json.JSONDecodeError:
            await update.message.reply_text("Lỗi: API trả về dữ liệu không hợp lệ")
        
        # Xóa tin nhắn đang xử lý
        await processing_msg.delete()
        
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        await update.message.reply_text(f"Đã xảy ra lỗi: {str(e)}")        
async def get_freefire_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lấy và hiển thị thông tin tài khoản Free Fire."""
    if not await check_authorized_group(update, context):
        return
    try:
        # Lấy UID từ tin nhắn
        if not context.args:
            await update.message.reply_text("Vui lòng cung cấp UID Free Fire. Ví dụ: /infoff 833822096")
            return

        # Lấy UID
        uid = context.args[0]
        
        # Kiểm tra UID có phải là số không
        if not uid.isdigit():
            await update.message.reply_text("UID không hợp lệ. UID phải là một dãy số.")
            return
        
        # Thông báo đang xử lý
        processing_msg = await update.message.reply_text(f"Đang lấy thông tin Free Fire cho UID {uid}...")
        
        # Tạo URL API với region mặc định là "vn"
        api_url = f"https://infoffvip.vercel.app/info?region=vn&uid={uid}"
        
        logging.info(f"Requesting Free Fire info API: {api_url}")
        
        # Gửi request đến API
        response = requests.get(api_url)
        
        # Kiểm tra response
        if response.status_code != 200:
            await update.message.reply_text(f"Lỗi: Không thể kết nối đến API. Mã lỗi: {response.status_code}")
            await processing_msg.delete()
            return
        
        # Parse JSON
        try:
            data = response.json()
            logging.info(f"Free Fire Info API Response: {json.dumps(data, indent=2)}")
            
            # Kiểm tra lỗi trong API response
            if data.get("error"):
                await update.message.reply_text(f"❌ Lỗi: {data.get('message', 'Không tìm thấy thông tin')}")
                await processing_msg.delete()
                return
            
            # Lấy các thông tin cơ bản
            basic_info = data.get("basicInfo", {})
            pet_info = data.get("petInfo", {})
            social_info = data.get("socialInfo", {})
            
            # Chuyển đổi timestamp thành ngày tháng năm nếu có
            create_date = "N/A"
            last_login = "N/A"
            
            if "createAt" in basic_info and basic_info["createAt"]:
                try:
                    create_timestamp = int(basic_info["createAt"])
                    create_date = datetime.datetime.fromtimestamp(create_timestamp).strftime('%d/%m/%Y')
                except:
                    create_date = str(basic_info["createAt"])
            
            if "lastLoginAt" in basic_info and basic_info["lastLoginAt"]:
                try:
                    login_timestamp = int(basic_info["lastLoginAt"])
                    last_login = datetime.datetime.fromtimestamp(login_timestamp).strftime('%d/%m/%Y')
                except:
                    last_login = str(basic_info["lastLoginAt"])
            
            # Xác định giới tính
            gender = "Nam" if social_info.get("gender") == "Gender_MALE" else "Nữ" if social_info.get("gender") == "Gender_FEMALE" else social_info.get("gender", "N/A")
            
            # Tạo thông tin cơ bản
            info_message = (
                f"🎮 THÔNG TIN FREE FIRE 🎮\n\n"
                f"📊 THÔNG TIN CƠ BẢN 📊\n"
                f"🆔 ID: {basic_info.get('uid', uid)}\n"
                f"👤 Nickname: {basic_info.get('nickname', 'N/A')}\n"
                f"🏆 Level: {basic_info.get('level', 'N/A')}\n"
                f"🌍 Khu vực: {basic_info.get('region', 'VN')}\n"
                f"📅 Ngày tạo: {create_date}\n"
                f"🕒 Đăng nhập cuối: {last_login}\n"
                f"⭐ Kinh nghiệm: {format(int(basic_info.get('exp', 0)), ',')}\n"
                f"🏅 Xếp hạng: {basic_info.get('rank', 'N/A')}\n"
                f"📈 Điểm xếp hạng: {format(int(basic_info.get('rankingPoints', 0)), ',')}\n"
                f"👍 Lượt thích: {format(int(basic_info.get('liked', 0)), ',')}\n"
                f"🏆 Mùa: {basic_info.get('seasonId', 'N/A')}\n"
            )
            
            # Thêm thông tin thú cưng nếu có
            if pet_info:
                pet_message = (
                    f"\n🐾 THÔNG TIN THÚ CƯNG 🐾\n"
                    f"🆔 ID: {pet_info.get('id', 'N/A')}\n"
                    f"📛 Tên: {pet_info.get('name', 'N/A')}\n"
                    f"🏆 Level: {pet_info.get('level', 'N/A')}\n"
                    f"⭐ Kinh nghiệm: {format(int(pet_info.get('exp', 0)), ',')}\n"
                )
                info_message += pet_message
            
            # Thêm thông tin xã hội
            if social_info:
                social_message = (
                    f"\n👥 THÔNG TIN XÃ HỘI 👥\n"
                    f"👤 Giới tính: {gender}\n"
                    f"🌐 Ngôn ngữ: {social_info.get('language', 'N/A')}\n"
                    f"🎮 Chế độ yêu thích: {social_info.get('modePrefer', 'N/A')}\n"
                    f"🏆 Hiển thị xếp hạng: {social_info.get('rankShow', 'N/A')}\n"
                )
                
                # Thêm chữ ký nếu có
                if "signature" in social_info and social_info["signature"]:
                    social_message += f"✏️ Chữ ký: \"{social_info['signature']}\"\n"
                
                info_message += social_message
            
            # Gửi thông tin
            await update.message.reply_text(info_message)
            
        except json.JSONDecodeError:
            await update.message.reply_text("Lỗi: API trả về dữ liệu không hợp lệ")
        except Exception as e:
            logging.error(f"Error parsing API response: {str(e)}")
            await update.message.reply_text(f"Lỗi khi xử lý dữ liệu: {str(e)}")
        
        # Xóa tin nhắn đang xử lý
        await processing_msg.delete()
        
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        await update.message.reply_text(f"Đã xảy ra lỗi: {str(e)}")
async def addfr(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Spam friend request cho tài khoản."""
    if not await check_authorized_group(update, context):
        return
    try:
        # Kiểm tra arguments
        if not context.args:
            await update.message.reply_text("⚠️ Vui lòng nhập UID.\nVí dụ: /addfr 12345678", 
                                           reply_to_message_id=update.message.message_id)
            return

        uid = context.args[0]
        
        # Thông báo đang xử lý
        processing_msg = await update.message.reply_text(f"Đang spam friend cho UID {uid}...")
        
        # Gửi request đến API
        url = f"https://spamfriend.vercel.app/addfriend?uid={uid}"
        logging.info(f"Requesting spam friend API: {url}")
        
        response = requests.get(url)
        
        # Kiểm tra response
        if response.status_code != 200:
            await update.message.reply_text("❌ Lỗi kết nối đến API. Vui lòng thử lại sau.", 
                                          reply_to_message_id=update.message.message_id)
            await processing_msg.delete()
            return
            
        # Parse JSON
        try:
            data = response.json()
            logging.info(f"Spam Friend API Response: {json.dumps(data, indent=2)}")
            
            if "status" in data and data["status"] == 0:
                await update.message.reply_text("❌ Lỗi. Kiểm tra UID hoặc thử lại sau.", 
                                              reply_to_message_id=update.message.message_id)
                await processing_msg.delete()
                return
            
            # Lấy thông tin
            nickname = data.get("nickname", "Không rõ")
            level = data.get("level", "Không rõ")
            region = data.get("region", "Không rõ")
            success_count = data.get("success_count", 0)
            sender_name = update.message.from_user.first_name
            
            # Tạo tin nhắn thành công
            success_message = (
                f"🔥 **Spam thành công** 🔥\n\n"
                f"- **Người Chơi:** ` {nickname}`\n"
                f"- **UID:** `{uid}`\n"
                f"- **Khu vực:** `{region}`\n"
                f"- **Cấp độ:** `{level}`\n"
                f"- **Số lượng:** `{success_count}`\n\n"
                f"**☠️Người gửi:** {sender_name}"
            )
            
            await update.message.reply_text(success_message, 
                                         parse_mode="HTML", 
                                         reply_to_message_id=update.message.message_id)
                                         
        except json.JSONDecodeError:
            await update.message.reply_text("❌ API trả về dữ liệu không hợp lệ")
            
        # Xóa tin nhắn đang xử lý
        await processing_msg.delete()
        
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        await update.message.reply_text("❌ Đã xảy ra lỗi. Vui lòng thử lại sau.",
                                     reply_to_message_id=update.message.message_id)
def main() -> None:
    """Khởi động bot."""
    try:
        # Tạo ứng dụng và lấy token
        application = Application.builder().token(TOKEN).build()

        # Thêm các handler
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("infotiktok", get_tiktok_info))
        application.add_handler(CommandHandler("videotiktok", get_tiktok_video_info))
        application.add_handler(CommandHandler("fl", increase_tiktok_followers))
        application.add_handler(CommandHandler("tpff", get_freefire_outfit))
        application.add_handler(CommandHandler("fb", get_facebook_info))
        application.add_handler(CommandHandler("viewff", get_freefire_views))
        application.add_handler(CommandHandler("infoff", get_freefire_info))
        application.add_handler(CommandHandler("addfr", addfr))

        # Khởi động bot
        print("Bot đang khởi động...")
        application.run_polling()
    except Exception as e:
        print(f"Lỗi khi khởi động bot: {str(e)}")

if __name__ == "__main__":
    main()