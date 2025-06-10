import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
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

def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\! '
        'Send me a MEGA\.nz link and I\'ll download it for you\.'
    )

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text(
        'Just send me a MEGA.nz file or folder link and I\'ll download it for you.\n\n'
        'Commands:\n'
        '/start - Start the bot\n'
        '/help - Show this help message\n\n'
        'Note: There is a 2GB file size limit.'
    )

def download_mega_file(update: Update, context: CallbackContext) -> None:
    """Download a file from MEGA.nz."""
    message = update.message
    url = message.text
    
    # Check if the message contains a MEGA URL
    if 'mega.nz' not in url.lower() and 'mega.co.nz' not in url.lower():
        message.reply_text("Please send a valid MEGA.nz URL.")
        return
    
    try:
        # Inform user that download is starting
        progress_msg = message.reply_text("Starting download...")
        
        # Initialize MEGA client
        mega = Mega()
        
        # Get public file info
        file_info = mega.get_public_file_info(url)
        file_name = file_info['name']
        file_size = file_info['size']
        
        # Check file size limit
        if file_size > MAX_FILE_SIZE:
            progress_msg.edit_text(f"File is too large ({file_size/1024/1024:.2f} MB). Max allowed is {MAX_FILE_SIZE/1024/1024:.2f} MB.")
            return
        
        # Update progress message
        progress_msg.edit_text(f"Downloading {file_name} ({file_size/1024/1024:.2f} MB)...")
        
        # Download the file
        downloaded_file = mega.download_url(url, DOWNLOAD_FOLDER)
        
        # Send the file to user
        with open(downloaded_file, 'rb') as f:
            context.bot.send_document(
                chat_id=message.chat_id,
                document=f,
                filename=file_name,
                caption=f"Here's your file: {file_name}"
            )
        
        # Clean up
        os.remove(downloaded_file)
        progress_msg.delete()
        
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        message.reply_text(f"Failed to download file. Error: {str(e)}")
        try:
            progress_msg.delete()
        except:
            pass

def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - check for MEGA links
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, download_mega_file))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
