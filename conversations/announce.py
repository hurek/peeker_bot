import json

from pony.orm import db_session, select
from telegram.ext import ConversationHandler
from conversations.conv_utils import ANNOUNCE
from configs.db_tools import User
from conversations.keyboards import back_kb, main_kb


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
    users = select(u for u in User)
    message = header + msg
    for user in users:
        context.bot.send_message(text=message, chat_id=user.telegram_id)
    context.bot.send_message(chat_id=274980096, text='Done!', reply_markup=main_kb)
    return ConversationHandler.END
