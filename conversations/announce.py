import json

from pony.orm import db_session, select
from telegram.ext import CommandHandler, ConversationHandler, Filters, MessageHandler
from conversations.conv_utils import ANNOUNCE, CHAT_TIMEOUT, cancel, chat_timeout
from configs.db_tools import *
from conversations.keyboards import back_kb


def announce(update, context):
    with open("configs/admins.json", 'r') as json_file:
        admins = json.load(json_file)
    if update.message.from_user.id not in [i["id"] for i in admins]:
        return
    update.message.reply_text('Enter announce:', reply_markup=back_kb)
    return ANNOUNCE


@db_session
def send_announce(update, context):
    header = "⭐️ANNOUNCEMENT⭐️\n\n"
    msg = update.message.text
    print(msg)
    users = select(u for u in User)
    message = header + msg
    for user in users:
        context.bot.send_message(text=message, chat_id=user.telegram_id)
    return ConversationHandler.END


announce_handler = ConversationHandler(
    entry_points=[CommandHandler("announce", announce)],
    states={
        ANNOUNCE: [MessageHandler(Filters.regex('^(⬅️Back)$'), cancel),
                        MessageHandler(Filters.text, send_announce)],
        ConversationHandler.TIMEOUT: [MessageHandler(Filters.text | Filters.command, chat_timeout)],
    },
    conversation_timeout=CHAT_TIMEOUT,
    fallbacks=[CommandHandler('cancel', cancel), MessageHandler(Filters.regex('^(⬅️Back)$'), cancel)],
)