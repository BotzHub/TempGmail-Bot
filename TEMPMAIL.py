import os
import logging
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot configuration
API_ID = int(os.environ.get("API_ID", 12345))
API_HASH = os.environ.get("API_HASH", "your_api_hash_here")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "your_bot_token_here")
REQUEST_CHANNEL = int(os.environ.get("REQUEST_CHANNEL", "-1001234567890"))  # Must start with -100
ADMIN_ID = int(os.environ.get("ADMIN_ID", "123456789"))  # Your Telegram ID

# Initialize the bot
app = Client(
    "RequestPickerBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

async def verify_channel_access():
    """Verify if bot has access to the request channel"""
    try:
        channel = await app.get_chat(REQUEST_CHANNEL)
        if channel.type not in (enums.ChatType.CHANNEL, enums.ChatType.SUPERGROUP):
            logger.error("REQUEST_CHANNEL must be a channel or supergroup")
            return False
        
        # Check if bot is admin
        me = await app.get_me()
        members = await app.get_chat_members(REQUEST_CHANNEL, filter=enums.ChatMembersFilter.ADMINISTRATORS)
        if not any(member.user.id == me.id for member in members):
            logger.error("Bot is not admin in the request channel")
            return False
            
        return True
    except Exception as e:
        logger.error(f"Channel verification failed: {e}")
        return False

# Start command handler
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        f"Hello ⏤‌‌•Ｓ𝙷𝚁𝙴𝚈𝙰𝙽𝚂𝙷 〄! 👋\n\n"
        f"I'm a Request Picker Bot. You can make requests using:\n"
        f"/r Movie/Show Name YYYY or\n"
        f"/request Movie/Show Name YYYY\n\n"
        f"You'll receive notifications when your requests are processed.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Support Group", url="https://t.me/yourgroup")]
        ])
    )

# Request command handler
@app.on_message(filters.command(["r", "request"]))
async def handle_request(client, message):
    try:
        if len(message.command) < 2:
            await message.reply_text("Please provide the name of the movie/show you're requesting.")
            return
            
        if not await verify_channel_access():
            await message.reply_text("⚠️ Bot configuration error. Admin has been notified.")
            await client.send_message(
                ADMIN_ID,
                "🚨 BOT CONFIGURATION REQUIRED\n\n"
                "1. Add bot to request channel as admin\n"
                "2. Enable permissions: Post Messages, Edit Messages\n"
                f"3. Current REQUEST_CHANNEL: {REQUEST_CHANNEL}"
            )
            return
            
        request_text = " ".join(message.command[1:])
        user = message.from_user
        
        request_msg = (
            f"📌 **New Request**\n\n"
            f"🎬 **Title:** {request_text}\n"
            f"👤 **User:** {user.mention}\n"
            f"🆔 **ID:** `{user.id}`\n"
            f"⏰ **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"#Request"
        )
        
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Received", callback_data=f"req_received:{user.id}:{request_text}"),
                InlineKeyboardButton("✅ Uploaded", callback_data=f"req_uploaded:{user.id}:{request_text}")
            ],
            [
                InlineKeyboardButton("⚠️ Available", callback_data=f"req_available:{user.id}:{request_text}"),
                InlineKeyboardButton("❌ Rejected", callback_data=f"req_rejected:{user.id}:{request_text}")
            ]
        ])
        
        try:
            msg = await client.send_message(
                chat_id=REQUEST_CHANNEL,
                text=request_msg,
                reply_markup=buttons
            )
            
            await message.reply_text(
                f"✅ Request submitted!\n\n"
                f"**Title:** {request_text}\n"
                f"**Status:** Pending review",
                reply_to_message_id=message.id
            )
            
        except Exception as e:
            logger.error(f"Failed to send to channel: {e}")
            await message.reply_text("⚠️ Failed to submit request. Trying alternative method...")
            await client.send_message(
                ADMIN_ID,
                f"🆘 MANUAL REQUEST NEEDED\n\n"
                f"From: {user.mention} (ID: {user.id})\n"
                f"Request: {request_text}\n\n"
                f"Error: {str(e)}"
            )

    except Exception as e:
        logger.error(f"Request handling error: {e}")
        await message.reply_text("An error occurred. Please try again later.")

# Callback query handler
@app.on_callback_query(filters.regex(r"^req_"))
async def handle_callback(client, callback_query):
    try:
        data = callback_query.data
        action, user_id, request_text = data.split(":")
        user_id = int(user_id)
        
        responses = {
            "req_received": "📥 Your request has been received and will be processed soon!",
            "req_uploaded": "🎉 Your requested content is now available!",
            "req_available": "ℹ️ This content is already available!",
            "req_rejected": "❌ Sorry, your request couldn't be fulfilled."
        }
        
        # Update channel message
        await callback_query.message.edit_text(
            f"{callback_query.message.text}\n\n"
            f"🔄 **Status:** {action.replace('_', ' ').title()}",
            reply_markup=None
        )
        
        # Notify user
        try:
            await client.send_message(
                chat_id=user_id,
                text=f"Regarding your request for **{request_text}**:\n\n{responses[action]}"
            )
        except Exception as e:
            logger.error(f"Failed to notify user: {e}")
            await callback_query.message.reply_text(
                f"⚠️ Couldn't notify user {user_id}\n"
                f"Error: {str(e)}"
            )
        
        await callback_query.answer("Status updated")
        
    except Exception as e:
        logger.error(f"Callback error: {e}")
        await callback_query.answer("Error processing this action", show_alert=True)

# Debug command
@app.on_message(filters.command("debug") & filters.user(ADMIN_ID))
async def debug(client, message):
    channel_status = await verify_channel_access()
    await message.reply_text(
        f"⚙️ Bot Debug Info\n\n"
        f"• Channel Access: {'✅' if channel_status else '❌'}\n"
        f"• REQUEST_CHANNEL: {REQUEST_CHANNEL}\n"
        f"• ADMIN_ID: {ADMIN_ID}\n"
        f"• Bot ID: {(await client.get_me()).id}"
    )

if __name__ == "__main__":
    logger.info("Starting Request Picker Bot...")
    app.run()
