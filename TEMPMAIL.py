import os
import random
import string
import re  # Regex to validate Gmail format
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler
from telegram.ext import ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Define states for the conversation
GMAIL, METHOD = range(2)

# Function to generate random name with 5 letters
def generate_random_name(length=5):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

# Function to generate variations of a Gmail address with exactly two dots
def generate_gmail_dot_variations(gmail: str, count: int = 50):
    if "@" not in gmail or gmail.count('@') != 1:  # Ensure valid format
        return ["❌ Invalid email format. Please enter a valid Gmail address."]

    local, domain = gmail.split('@')

    if domain != 'gmail.com':
        return ["❌ This bot works only with Gmail addresses."]

    variations = set()  # Use a set to avoid duplicates
    n = len(local)

    # Generate variations with exactly two dots
    for i in range(1, n):  # First dot can be placed from position 1 to n-1
        for j in range(i + 1, n + 1):  # Second dot must be after the first dot
            variation = local[:i] + '.' + local[i:j] + '.' + local[j:] + '@' + domain
            variations.add(variation)
            if len(variations) >= count:  # Stop generating if we have enough variations
                break
        if len(variations) >= count:
            break

    return list(variations)[:count]  # Return only the requested number of variations

# Function to generate variations using the + (random name) method
def generate_gmail_plus_variations(gmail: str, count: int = 50):
    if "@" not in gmail or gmail.count('@') != 1:  # Ensure valid format
        return ["❌ Invalid email format. Please enter a valid Gmail address."]

    local, domain = gmail.split('@')

    if domain != 'gmail.com':
        return ["❌ This bot works only with Gmail addresses."]

    variations = set()  # Use a set to avoid duplicates

    for _ in range(count):
        random_name = generate_random_name()
        variation = f"{local}+{random_name}@{domain}"
        variations.add(variation)

    return list(variations)  # Return all generated variations

# Escape special characters for MarkdownV2
def escape_markdown_v2(text: str) -> str:
    return text.replace('.', '\\.').replace('-', '\\-').replace('+', '\\+').replace('@', '\\@').replace('_', '\\_')

# Start command to welcome users
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/SmartEdith_Bot"), InlineKeyboardButton("📢 Join Channel", url="https://t.me/Tech_Shreyansh")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        '🤖 Welcome! Bot Made By - Shreyansh\n'
        "📄 Only Gmails Are Supported\n"
        "📝 Please Enter Your Gmail Address.",
        parse_mode="HTML",
        reply_markup=reply_markup
    )
    return GMAIL  # Move to the next step

# Function to handle the Gmail input
async def handle_gmail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:  # Check if message exists
        return GMAIL  # Ignore invalid updates

    user_gmail = update.message.text.strip()
    
    # Validate Gmail format
    if not re.match(r'^[a-zA-Z0-9._%+-]+@gmail\.com$', user_gmail):
        await update.message.reply_text("❌ Invalid Gmail format. Please enter a valid Gmail address.")
        return GMAIL  # Stay in the GMAIL state if invalid input
    
    context.user_data['gmail'] = user_gmail  # Store the Gmail address
    await update.message.reply_text(
        "✅ Gmail saved! Now please choose the method for generating variations:\n"
        "1️⃣ Type 'dot' for dot variations.\n"
        "2️⃣ Type '+' for random name variations.\n"
        "3️⃣ Press /start to reselect Gmail."
    )
    return METHOD  # Move to the next step

# Function to handle the method input and generate 50 variations
async def handle_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:  # Check if message exists
        return METHOD  # Ignore invalid updates

    method = update.message.text.lower().strip()
    
    if method not in ['dot', '+']:
        await update.message.reply_text("❌ Invalid method. Please enter 'dot' or '+' for variation generation.")
        return METHOD  # Stay in the METHOD state if invalid input

    if 'gmail' not in context.user_data:  # Check if Gmail is stored
        await update.message.reply_text("❌ No Gmail found. Please restart with /start.")
        return ConversationHandler.END

    gmail_address = context.user_data['gmail']  # Retrieve the stored Gmail address
    
    try:
        # Generate 50 variations based on the chosen method
        if method == 'dot':
            variations = generate_gmail_dot_variations(gmail_address, count=50)
        elif method == '+':
            variations = generate_gmail_plus_variations(gmail_address, count=50)

        if not variations:
            await update.message.reply_text("❌ No variations generated.")
        else:
            # Format variations for MarkdownV2 with proper escaping
            response = '\n'.join(f"`{escape_markdown_v2(variation)}`" for variation in variations)
            await update.message.reply_text(response, parse_mode='MarkdownV2')

    except Exception as e:
        await update.message.reply_text(f"❌ An error occurred: {str(e)}")
    
    return ConversationHandler.END  # End the conversation

# Function to cancel the conversation
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Conversation cancelled.")
    return ConversationHandler.END  # End the conversation

# Main function to run the bot
def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")  # Fetch the bot token from environment variable

    # Create the application
    app = ApplicationBuilder().token(token).build()

    # Set up the conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_gmail)],
            METHOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_method)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    # Add the conversation handler to the application
    app.add_handler(conv_handler)

    # Start the bot
    app.run_polling()

if __name__ == '__main__':
    main()
