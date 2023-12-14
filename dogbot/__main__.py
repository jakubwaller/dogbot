import datetime
import html
import json
import logging
import pandas as pd
import random
import traceback
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

from tools import run_request, read_config

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

csv_file_name = "logs/dog_bot_logs.csv"
df_columns = ["group", "timestamp", "breed", "gif"]

config = read_config()
developer_chat_id = config["developer_chat_id"]
bot_token = config["bot_token"]
dog_api_key = config["dog_api_key"]

try:
    df = pd.read_csv(csv_file_name)
except Exception:
    df = pd.DataFrame(columns=df_columns)

breeds_full = run_request("GET", "https://api.thedogapi.com/v1/breeds")


def senddogbybreed(update: Update, context: CallbackContext) -> None:
    """Sends a message with inline buttons attached."""
    keyboard = [
        InlineKeyboardButton(breed["name"], callback_data=breed["name"] + "__" + str(breed["id"]))
        for breed in breeds_full
    ]

    random.shuffle(keyboard)

    chunk_size = 3
    chunks = [keyboard[x : x + chunk_size] for x in range(0, len(keyboard), chunk_size)]

    reply_markup = InlineKeyboardMarkup(chunks)
    logger.info("called breed")
    update.message.reply_text("Please choose:", reply_markup=reply_markup)


def button(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    breed_name = query.data.split("__")[0]
    breed_id = query.data.split("__")[1]
    query.edit_message_text(text=f"Sending breed: {breed_name}")
    update.message = query.message
    update.message.from_user = query.from_user
    senddog(update, context, breed=breed_id)


def hi(update: Update, context: CallbackContext) -> None:
    """Displays info on how to use the bot."""
    update.message.reply_text("Hi there! I'm a DogBot and can send images of dogs.")


def senddoggif(update: Update, context: CallbackContext) -> None:
    """Sends a dog gif."""
    senddog(update, context, gif=True)


def senddog(update: Update, context: CallbackContext, breed=None, gif=False) -> None:
    """Sends a dog."""

    if breed:
        suffix = f"?breed_ids={breed}"
    else:
        suffix = ""
        breed = "random"

    if gif:
        suffix = "?mime_types=gif"
    elif len(suffix) == 0:
        suffix = "?mime_types=jpg,png"

    logger.info(suffix)

    num_of_max_tries = 5
    num_of_tries = 1
    success = False

    while num_of_tries <= num_of_max_tries and not success:
        try:
            num_of_tries += 1

            url = run_request(
                "GET",
                f"https://api.thedogapi.com/v1/images/search{suffix}",
                num_of_tries=5,
                request_headers={"Content-Type": "application/json", "x-api-key": dog_api_key},
            )[0]["url"]

            if url.endswith(".gif"):
                context.bot.send_animation(update.message.chat.id, url)
            else:
                context.bot.send_photo(update.message.chat.id, url)

            success = True
        except Exception as e:
            if num_of_tries == num_of_max_tries:
                raise e
            else:
                logger.error(e)

    global df

    try:
        if "group" in update.message.chat.type:
            is_group = True
        else:
            is_group = False
    except Exception as e:
        logger.error(e)
        is_group = False

    df = pd.concat([df, pd.DataFrame([[is_group, datetime.datetime.now(), breed, gif]], columns=df_columns)])
    df.to_csv(csv_file_name, header=True, index=False)

    if is_group:
        is_group_text = "a group"
    else:
        is_group_text = "a single user"
    context.bot.send_message(developer_chat_id, f"Sending a dog to {is_group_text}.")


def error_handler(update: object, context: CallbackContext) -> None:
    """Log the error and send a telegram message to notify the developer."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    context.bot.send_message(chat_id=developer_chat_id, text=str(context.error))


def main() -> None:
    """Setup and run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(bot_token)

    updater.dispatcher.add_handler(CommandHandler("hi", hi))
    updater.dispatcher.add_handler(CommandHandler("senddog", senddog))
    updater.dispatcher.add_handler(CommandHandler("senddoggif", senddoggif))
    updater.dispatcher.add_handler(CommandHandler("senddogbybreed", senddogbybreed))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    updater.dispatcher.add_error_handler(error_handler)

    # Start the Bot
    updater.start_polling(poll_interval=1)

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == "__main__":
    main()
