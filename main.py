"""The main script that runs it includes handlers, starts the scheduler, and starts the bot."""
import logging

from pony.orm import commit, db_session
from telegram.ext import CallbackQueryHandler, CommandHandler, Filters, MessageHandler, Updater
from telegram.utils.request import Request
from polog.flog import flog
from telegram.utils.webhookhandler import WebhookHandler

from configs.config import TOKEN
from configs.db_tools import User
from conversations.handlers import AnnounceHandler, FeedbackHandler, NewAddressHandler, RenameOperatorHandler, \
    UserGuideHandler
from conversations.keyboards import BACK, CLOSE, CONFIGURE, DELETE, DONATIONS, EXPLORER, LANGUAGE, user_guide_inline_kb
from conversations.my_adresses import delete_user_address, inline_back, inline_close, inline_configure, my_addresses, \
    subscribe_event
from conversations.settings import donate, explorers, language_set, settings
from notifications.MQbot import MQBot, mq
from conversations.conv_utils import main_kb, subscribe_event_dict

# Logger settings
from notifications.event_manager import collateralization, event_manager
from notifications.event_types import EventTypes
from notifications.node_status import check_status

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def buttons_dict():
    dictionary = {
        inline_configure: str(CONFIGURE),
        inline_close: str(CLOSE),
        inline_back: str(BACK),
        explorers: str(EXPLORER),
        language_set: str(LANGUAGE),
        donate: str(DONATIONS),
        delete_user_address: str(DELETE)
    }
    return dictionary


def conversation_handlers():
    handlers_list = [
        AnnounceHandler,
        NewAddressHandler,
        FeedbackHandler,
        RenameOperatorHandler,
        UserGuideHandler
    ]
    return handlers_list


@db_session
def start(update, context):
    if not (p := User.get(telegram_id=update.message.chat_id)):
        p = User(telegram_id=update.message.from_user.id)
        if update.message.from_user.username:
            p.username = update.message.from_user.id
        commit()
    update.message.reply_text(text='Hello 👋 I am a beta release of Peeker bot. For this reason if you have any '
                                   'suggestions or ideas you may contact to my creator👨‍💻.\n\nMy specific feature '
                                   'is delicate adjustment ⚙️ of notificationss for every operator address. I already '
                                   'know how to send several types of notificationss, but in the very near future I '
                                   'will learn how to do a lot more!',
                              reply_markup=user_guide_inline_kb) #TODO change to main


@flog
@db_session
def main():
    q = mq.MessageQueue(all_burst_limit=20, all_time_limit_ms=1500)
    request = Request(con_pool_size=8)
    peeker_bot = MQBot(TOKEN, request=request, mqueue=q)
    updater = Updater(bot=peeker_bot, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.regex('^(📖My Addresses)$'), my_addresses))

    for i in conversation_handlers():
        dp.add_handler(i())
    for key, value in buttons_dict().items():
        pattern = '^' + value + '$'
        dp.add_handler(CallbackQueryHandler(key, pattern=pattern))
    for key in subscribe_event_dict().keys():
        pattern = '^' + key + '$'
        dp.add_handler(CallbackQueryHandler(subscribe_event, pattern=pattern))

    dp.add_handler(MessageHandler(Filters.regex('^(⚙️Settings)$'), settings))

    updater.job_queue.run_repeating(event_manager, 60, name='Global events polling', job_kwargs={"misfire_grace_time": 15})
    updater.job_queue.run_repeating(collateralization, 90, name='C-Ratio polling', job_kwargs={"misfire_grace_time": 30})
    updater.job_queue.run_repeating(check_status, 300, name='Node status polling', job_kwargs={"misfire_grace_time": 20})
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()