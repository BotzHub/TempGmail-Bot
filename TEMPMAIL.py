import os
import json
import time
from telethon import TelegramClient, events, Button

# Configuration
API_ID = int(os.getenv('API_ID', 12345))
API_HASH = os.getenv('API_HASH', 'your_api_hash')
BOT_TOKEN = os.getenv('BOT_TOKEN', 'your_bot_token')
DATA_FILE = 'whispers.json'

# Initialize client
bot = TelegramClient('whisper_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

def save_whisper(timestamp, recipient_id, message):
    """Save whisper to JSON file"""
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    
    data[str(timestamp)] = {
        'recipient_id': recipient_id,
        'message': message
    }
    
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

def get_whisper(timestamp):
    """Retrieve whisper from JSON file"""
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            return data.get(str(timestamp))
    except (FileNotFoundError, json.JSONDecodeError):
        return None

@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    """Handle /start command"""
    help_text = (
        "👋 Welcome to Whisper Bot!\n\n"
        "Send private messages that only the recipient can view.\n\n"
        "📌 How to use:\n"
        "1. Reply to a user's message with /whisper <your message>\n"
        "2. Or mention them: /whisper @username <your message>\n\n"
        "Only the recipient can view the message when they click the button."
    )
    await event.respond(help_text)

@bot.on(events.NewMessage(pattern='/whisper'))
async def whisper_handler(event):
    """Handle whisper command"""
    # Parse command
    try:
        parts = event.raw_text.split(' ', 2)
        if len(parts) < 3:
            raise ValueError
        
        _, recipient_ref, message = parts
        
        # Get recipient
        if recipient_ref.startswith('@'):
            # Get by username
            recipient = await bot.get_entity(recipient_ref)
        elif event.is_reply:
            # Get from reply
            recipient = await event.get_reply_message()
            recipient = await bot.get_entity(recipient.sender_id)
            message = event.raw_text.split(' ', 1)[1]  # Get full message
        else:
            raise ValueError
        
        recipient_id = recipient.id
    except (ValueError, IndexError):
        await event.respond("Invalid format. Use:\n/whisper @username message\nor reply to a message with /whisper message")
        return
    except Exception as e:
        await event.respond(f"Error: {str(e)}")
        return

    # Create whisper
    timestamp = int(time.time())
    save_whisper(timestamp, recipient_id, message)
    
    # Create response
    if recipient.username:
        name = f"@{recipient.username}"
    else:
        name = recipient.first_name
    
    response = (
        f"🔒 A private message for {name}\n"
        "Only they can view it by clicking below."
    )
    
    await event.respond(
        response,
        buttons=Button.inline("👀 View Message", data=f"whisper_{timestamp}")
    )

@bot.on(events.CallbackQuery(data=re.compile(b'whisper_(\d+)')))
async def view_whisper_handler(event):
    """Handle whisper view callback"""
    timestamp = int(event.pattern_match.group(1).decode())
    whisper = get_whisper(timestamp)
    
    if not whisper:
        await event.answer("This message no longer exists.", alert=True)
        return
    
    # Check if user is the recipient
    if event.sender_id != whisper['recipient_id']:
        await event.answer("This message is not for you.", alert=True)
        return
    
    # Show the message
    await event.answer(whisper['message'], alert=True)

def main():
    """Start the bot"""
    print("🤫 Whisper Bot is running...")
    bot.run_until_disconnected()

if __name__ == '__main__':
    # Create empty data file if it doesn't exist
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump({}, f)
    
    main()
