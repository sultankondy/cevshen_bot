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
CHAT_ID = int(os.getenv("CHAT_ID"))  # must be int

# Names and ranges
names = ["Sultan", "Muhit", "Rustem", "Shadiar", "Dias", "Daniel", "Kuanysh"]
ranges = ["1-15", "16-30", "31-45", "46-60", "61-75", "76-90", "91-100 + dua"]

def generate_poll_options():
    today = datetime.date.today()
    weekday = today.weekday()  # Monday = 0, ..., Sunday = 6
    sultan_index = names.index("Sultan")
    shift = (sultan_index - ((weekday - 2) % 7)) % 7

    rotated_names = names[shift:] + names[:shift]
    options = [f"{name} {rng}" for name, rng in zip(rotated_names, ranges)]
    title = today.strftime("%B %d")
    return title, options

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    title, options = generate_poll_options()
    await context.bot.send_poll(
        chat_id=update.effective_chat.id,
        question=title,
        options=options,
        is_anonymous=False,
        allows_multiple_answers=False
    )

async def send_daily_poll(app: Application):
    title, options = generate_poll_options()
    await app.bot.send_poll(
        chat_id=CHAT_ID,
        question=title,
        options=options,
        is_anonymous=False,
        allows_multiple_answers=False
    )

async def run_scheduler(app: Application):
    schedule.every().day.at("09:00").do(lambda: asyncio.create_task(send_daily_poll(app)))
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    # Run scheduler + polling in parallel
    await asyncio.gather(
        app.run_polling(),
        run_scheduler(app)
    )

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(main())
        else:
            loop.run_until_complete(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped.")
