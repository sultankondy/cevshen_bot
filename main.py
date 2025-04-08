import os
import datetime
import asyncio
import schedule
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # must be an integer

# Names and ranges
names = ["Sultan", "Muhit", "Rustem", "Shadiar", "Dias", "Daniel", "Kuanysh"]
ranges = ["1-15", "16-30", "31-45", "46-60", "61-75", "76-90", "91-100 + dua"]

def generate_poll_options():
    today = datetime.date.today()
    weekday = today.weekday()  # 0=Monday, 1=Tuesday, ..., 6=Sunday
    sultan_index = names.index("Shadiar")
    shift = (sultan_index - ((weekday - 2) % 7)) % 7

    # Rotate names
    rotated_names = names[shift:] + names[:shift]

    # Fixed range order (1-15, 16-30, 31-45, 46-60, 61-75, 76-90, 91-100 + dua)
    ordered_ranges = ranges

    # Combine rotated names with ordered ranges
    options = [f"{name} {rng}" for name, rng in zip(rotated_names, ordered_ranges)]
    
    # Use the current date as the title
    title = today.strftime("%B %d")
    
    return title, options

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    title, options = generate_poll_options()
    await context.bot.send_poll(
        chat_id=update.effective_chat.id,
        question=title,
        options=options,
        is_anonymous=False,
        allows_multiple_answers=False
    )

# Scheduled daily poll sender
async def send_daily_poll(app: Application):
    title, options = generate_poll_options()
    await app.bot.send_poll(
        chat_id=CHAT_ID,
        question=title,
        options=options,
        is_anonymous=False,
        allows_multiple_answers=False
    )

# Scheduler runner
async def run_scheduler(app: Application):
    schedule.every().day.at("09:00").do(lambda: asyncio.create_task(send_daily_poll(app)))
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

# Main function (manually start everything)
async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    await app.initialize()
    await app.start()
    print("Bot is running...")

    asyncio.create_task(run_scheduler(app))

    # Keep the bot running (non-blocking polling)
    await app.updater.start_polling()
    await asyncio.Event().wait()  # keeps loop alive forever

# Run in macOS-compatible way
if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("Bot stopped.")
