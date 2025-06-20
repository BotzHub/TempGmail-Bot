import os
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot configuration
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
REQUEST_CHANNEL = os.environ.get("REQUEST_CHANNEL", "-1001234567890")  # Channel where requests will be forwarded
ADMIN_ID = int(os.environ.get("ADMIN_ID", "123456789"))  # Your Telegram ID

# Initialize the bot
app = Client(
    "RequestPickerBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Start command handler
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        f"Hello ⏤‌‌•Ｓ𝙷𝚁𝙴𝚈𝙰𝙽𝚂𝙷 〄! 👋\n\n"
        f"I'm a Request Picker Bot. You can make requests in our group using:\n"
        f"/r Movie/Show Name YYYY or\n"
        f"/request Movie/Show Name YYYY\n\n"
        f"You'll receive notifications here when your requests are processed.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Support Group", url="https://t.me/yourgroup")]
        ])
    )

# Request command handler
@app.on_message(filters.command(["r", "request"]))
async def handle_request(client, message):
    try:
        # Extract the request text
        if len(message.command) < 2:
            await message.reply_text("Please provide the name of the movie/show you're requesting.")
            return
            
        request_text = " ".join(message.command[1:])
        user = message.from_user
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Format the request message
        request_msg = (
            f"📌 **New Request**\n\n"
            f"🎬 **Title:** {request_text}\n"
            f"👤 **User:** {user.mention}\n"
            f"🆔 **User ID:** `{user.id}`\n"
            f"⏰ **Time:** {timestamp}\n\n"
            f"#Request"
        )
        
        # Create buttons for admin actions
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Request Received", callback_data=f"req_received:{user.id}:{request_text}"),
                InlineKeyboardButton("✅ Upload Done", callback_data=f"req_uploaded:{user.id}:{request_text}")
            ],
            [
                InlineKeyboardButton("⚠️ Already Available", callback_data=f"req_available:{user.id}:{request_text}"),
                InlineKeyboardButton("❌ Reject Request", callback_data=f"req_rejected:{user.id}:{request_text}")
            ]
        ])
        
        try:
            # Forward the request to the channel
            await client.send_message(
                chat_id=REQUEST_CHANNEL,
                text=request_msg,
                reply_markup=buttons
            )
        except Exception as channel_error:
            logger.error(f"Channel access error: {channel_error}")
            # If private channel access fails, notify admin
            await client.send_message(
                chat_id=ADMIN_ID,
                text=f"⚠️ Bot failed to access request channel {REQUEST_CHANNEL}. Error: {channel_error}"
            )
            await message.reply_text(
                "⚠️ Our system is currently experiencing issues. The admin has been notified."
            )
            return
        
        # Confirm to the user
        await message.reply_text(
            f"✅ Your request for **{request_text}** has been submitted!\n\n"
            f"You'll be notified here when it's processed.",
            reply_to_message_id=message.id
        )
        
    except Exception as e:
        logger.error(f"Error handling request: {e}")
        await message.reply_text("An error occurred while processing your request. Please try again.")

# Callback query handler
@app.on_callback_query()
async def handle_callback(client, callback_query):
    try:
        data = callback_query.data
        action, user_id, request_text = data.split(":")
        user_id = int(user_id)
        
        # Define responses for different actions
        responses = {
            "req_received": f"📥 Your request for **{request_text}** has been received and will be processed soon!",
            "req_uploaded": f"🎉 Good news! Your requested content **{request_text}** is now available!",
            "req_available": f"ℹ️ Your requested content **{request_text}** is already available in our database!",
            "req_rejected": f"❌ Sorry, your request for **{request_text}** couldn't be fulfilled at this time."
        }
        
        try:
            # Send notification to user
            await client.send_message(
                chat_id=user_id,
                text=responses.get(action, "Your request status has been updated.")
            )
        except Exception as user_msg_error:
            logger.error(f"Failed to message user {user_id}: {user_msg_error}")
            await callback_query.answer("Failed to notify user. They may have blocked the bot.")
            return
        
        # Update the original message in the channel
        try:
            await callback_query.message.edit_text(
                f"{callback_query.message.text}\n\n"
                f"🔄 **Status:** {action.replace('_', ' ').title()}",
                reply_markup=None
            )
        except Exception as edit_error:
            logger.error(f"Failed to edit message: {edit_error}")
            await callback_query.answer("Action processed but failed to update channel message.")
            return
        
        # Answer the callback query
        await callback_query.answer(f"User notified about {action.replace('_', ' ')}")
        
    except Exception as e:
        logger.error(f"Error handling callback: {e}")
        await callback_query.answer("An error occurred while processing this action.")

# Start the bot
if __name__ == "__main__":
    logger.info("Starting Request Picker Bot...")
    app.run()
