import pyrogram
import os
import requests
from PIL import Image
from io import BytesIO

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
<b>I am a poster bot</b>
<b>Send me /poster <movie_name> to get the movie poster!</b>
<b>@Ms_Update_channel</b>"""

about_message = """
<b>• Name : [AutoCaption V1](t.me/{username})</b>
<b>• Developer : [Muhammed](https://github.com/PR0FESS0R-99)</b>
<b>• Language : Python3</b>
<b>• Library : Pyrogram v{version}</b>
<b>• Updates : <a href=https://t.me/Mo_Tech_YT>Click Here</a></b>
<b>• Source Code : <a href=https://github.com/PR0FESS0R-99/AutoCaption-Bot>Click Here</a></b>"""

@posterbot.on_message(pyrogram.filters.private & pyrogram.filters.command(["start"]))
def start_command(bot, update):
    update.reply(start_message.format(update.from_user.mention), reply_markup=start_buttons(bot, update), parse_mode=pyrogram.enums.ParseMode.HTML, disable_web_page_preview=True)

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

    # Construct URL for original size poster
    poster_url = f"https://image.tmdb.org/t/p/original{poster_path}"

    # Send the poster as a thumbnail view
    await bot.send_photo(chat_id=message.chat.id, photo=poster_url, caption=f"Poster of {movie['title']}", thumb=poster_url)

def start_buttons(bot, update):
    bot = bot.get_me()
    buttons = [[
        pyrogram.types.InlineKeyboardButton("Updates", url="t.me/Mo_Tech_YT"),
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

print("Telegram poster bot Start")
print("Bot Created By https://github.com/PR0FESS0R-99")

posterbot.run()
