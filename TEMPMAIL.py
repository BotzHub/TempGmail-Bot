import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from mega import Mega

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
TOKEN = '8145714862:AAHJobXXT_M7QdT5Hi4y1jof31Sj5ojw_cc'
DOWNLOAD_FOLDER = 'downloads'
MAX_FILE_SIZE = 2000 * 1024 * 1024  # 2GB limit

# Create download folder if it doesn't exist
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\! '
        'Send me a MEGA\.nz link and I\'ll download it for you\.'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        'Just send me a MEGA.nz file or folder link and I\'ll download it for you.\n\n'
        'Commands:\n'
        '/start - Start the bot\n'
        '/help - Show this help message\n\n'
        'Note: There is a 2GB file size limit.'
    )

async def download_mega_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Download a file from MEGA.nz."""
    message = update.message
    url = message.text
    
    # Check if the message contains a MEGA URL
    if 'mega.nz' not in url.lower() and 'mega.co.nz' not in url.lower():
        await message.reply_text("Please send a valid MEGA.nz URL.")
        return
    
    try:
        # Inform user that download is starting
        progress_msg = await message.reply_text("Starting download...")
        
        # Initialize MEGA client
        mega = Mega()
        
        # Get public file info
        file_info = mega.get_public_file_info(url)
        file_name = file_info['name']
        file_size = file_info['size']
        
        # Check file size limit
        if file_size > MAX_FILE_SIZE:
            await progress_msg.edit_text(f"File is too large ({file_size/1024/1024:.2f} MB). Max allowed is {MAX_FILE_SIZE/1024/1024:.2f} MB.")
            return
        
        # Update progress message
        await progress_msg.edit_text(f"Downloading {file_name} ({file_size/1024/1024:.2f} MB)...")
        
        # Download the file
        downloaded_file = mega.download_url(url, DOWNLOAD_FOLDER)
        
        # Send the file to user
        with open(downloaded_file, 'rb') as f:
            await context.bot.send_document(
                chat_id=message.chat_id,
                document=f,
                filename=file_name,
                caption=f"Here's your file: {file_name}"
            )
        
        # Clean up
        os.remove(downloaded_file)
        await progress_msg.delete()
        
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        await message.reply_text(f"Failed to download file. Error: {str(e)}")
        try:
            await progress_msg.delete()
        except:
            pass

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = ApplicationBuilder().token(TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_mega_file))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == '__main__':
    main()
