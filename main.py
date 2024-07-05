import os
import re
import requests
from PIL import Image
from io import BytesIO
import threading
from flask import Flask
import pyrogram

# Initialize Flask app
app = Flask(__name__)

try:
    app_id = int(os.environ.get("app_id"))
    api_hash = os.environ.get("api_hash")
    bot_token = os.environ.get("bot_token")
    tmdb_api_key = "1b379a6e5e53d2282de8d79772f47f79"
except Exception as e:
    print(f"⚠️ Error in environment variables: {e}")

posterbot = pyrogram.Client(
    name="posterbot", api_id=app_id, api_hash=api_hash, bot_token=bot_token)

start_message = """
<b>👋Hello {}</b>
<b>I am a Movie Poster bot</b>
<b>Send me /poster <movie_name> to get the movie poster</b>
<b>@Ms_Update_channel</b>"""

about_message = """
<b>• Name : [MoviePosterBot](t.me/{username})</b>
<b>• Developer : [Your Name](https://github.com/YourUsername)</b>
<b>• Language : Python3</b>
<b>• Library : Pyrogram v{version}</b>
<b>• Updates : <a href=https://t.me/Your_Channel>Click Here</a></b>
<b>• Source Code : <a href=https://github.com/YourUsername/MoviePosterBot>Click Here</a></b>"""

@posterbot.on_message(pyrogram.filters.private & pyrogram.filters.command(["start"]))
def start_command(bot, message):
    message.reply(start_message.format(message.from_user.mention), reply_markup=start_buttons(bot, message), parse_mode=pyrogram.enums.ParseMode.HTML, disable_web_page_preview=True)

@posterbot.on_callback_query(pyrogram.filters.regex("start"))
def start_callback(bot, update):
    update.message.edit(start_message.format(update.from_user.mention), reply_markup=start_buttons(bot, update.message), parse_mode=pyrogram.enums.ParseMode.HTML, disable_web_page_preview=True)

@posterbot.on_callback_query(pyrogram.filters.regex("about"))
def about_callback(bot, update): 
    bot = bot.get_me()
    update.message.edit(about_message.format(version=pyrogram.__version__, username=bot.mention), reply_markup=about_buttons(bot, update.message), parse_mode=pyrogram.enums.ParseMode.HTML, disable_web_page_preview=True)

@posterbot.on_message(pyrogram.filters.private & pyrogram.filters.command(["poster"]))
async def poster_command(bot, message):
    query = message.text[len('/poster '):].strip()
    if not query:
        await message.reply("Please provide a movie name after the command, e.g., /poster Pushpa")
        return

    tmdb_url = f"https://api.themoviedb.org/3/search/movie?api_key={tmdb_api_key}&query={query}"
    response = requests.get(tmdb_url)
    if response.status_code != 200:
        await message.reply("Error fetching movie details. Please try again.")
        return

    data = response.json()
    if not data['results']:
        await message.reply("Movie not found. Please check the name and try again.")
        return

    movie = data['results'][0]
    poster_path = movie.get('poster_path')
    if not poster_path:
        await message.reply("No poster available for this movie.")
        return

    poster_url = f"https://image.tmdb.org/t/p/w1280{poster_path}"
    poster_response = requests.get(poster_url)
    if poster_response.status_code != 200:
        await message.reply("Error fetching the movie poster. Please try again.")
        return

    image = Image.open(BytesIO(poster_response.content))
    if image.size != (1280, 720):
        image = image.resize((1280, 720))

    with BytesIO() as output:
        image.save(output, format="JPEG")
        output.seek(0)
        await bot.send_photo(chat_id=message.chat.id, photo=output, caption=f"Poster of {movie['title']}")

def start_buttons(bot, update):
    bot = bot.get_me()
    buttons = [[
        pyrogram.types.InlineKeyboardButton("Updates", url="t.me/Your_Channel"),
        pyrogram.types.InlineKeyboardButton("About 🤠", callback_data="about")
    ],[
        pyrogram.types.InlineKeyboardButton("➕️ Add To Your Channel ➕️", url=f"http://t.me/{bot.username}?startchannel=true")
    ]]
    return pyrogram.types.InlineKeyboardMarkup(buttons)

def about_buttons(bot, update):
    buttons = [[
        pyrogram.types.InlineKeyboardButton("🏠 Back To Home 🏠", callback_data="start")
    ]]
    return pyrogram.types.InlineKeyboardMarkup(buttons)

# Flask route for web support
@app.route('/')
def home():
    return "Bot is running!"

def run_bot():
    print("Telegram MoviePosterBot Start")
    print("Bot Created By https://github.com/YourUsername")
    posterbot.run()

if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    app.run(host='0.0.0.0', port=8080)
