"""The main script that runs it includes handlers, starts the scheduler, and starts the bot."""
import logging

from telegram.ext import Updater
from telegram.utils.request import Request
from polog.flog import flog
from configs.config import TOKEN
from conversations.announce import announce_handler
from conversations.my_adresses import *
from conversations.new_address import *
from conversations.feedback import *
from conversations.settings import *
from notifications.MQbot import MQBot, mq
from notifications.event_manager import *


# Logger settings
from notifications.node_status import check_status

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


@db_session
def start(update, context):
    if not (p := User.get(telegram_id=update.message.chat_id)):
        p = User(telegram_id=update.message.from_user.id, username=update.message.from_user.username)
        commit()
    update.message.reply_text(text='Hello 👋 I am a beta release of Peeker bot. For this reason if you have any '
                                   'suggestions or ideas you may contact to my creator👨‍💻.\n\nMy specific feature '
                                   'is delicate adjustment ⚙️ of notificationss for every operator address. I already '
                                   'know how to send several types of notificationss, but in the very near future I '
                                   'will learn how to do a lot more!',
                              reply_markup=main_kb)


@flog
@db_session
def main():
    q = mq.MessageQueue(all_burst_limit=20, all_time_limit_ms=1500)
    request = Request(con_pool_size=8)
    peeker_bot = MQBot(TOKEN, request=request, mqueue=q)
    updater = Updater(bot=peeker_bot, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(announce_handler)
    dp.add_handler(new_address_handler)
    dp.add_handler(feedback_handler)

    dp.add_handler(MessageHandler(Filters.regex('^(📖My Addresses)$'), my_addresses))
    dp.add_handler(CallbackQueryHandler(inline_configure, pattern='^' + str(CONFIGURE) + '$'))
    dp.add_handler(CallbackQueryHandler(inline_close, pattern='^' + str(CLOSE) + '$'))
    dp.add_handler(CallbackQueryHandler(inline_back, pattern='^' + str(BACK) + '$'))


    event_dict = subscribe_event_dict()
    for key in event_dict.keys():
        pattern = '^' + key + '$'
        dp.add_handler(CallbackQueryHandler(subscribe_event, pattern=pattern))

    dp.add_handler(CallbackQueryHandler(delete_user_address, pattern='^' + str(DELETE) + '$'))
    dp.add_handler(rename_operator_handler)

    dp.add_handler(MessageHandler(Filters.regex('^(⚙️Settings)$'), settings))
    dp.add_handler(CallbackQueryHandler(explorers, pattern='^' + str(EXPLORER) + '$'))
    dp.add_handler(CallbackQueryHandler(language_set, pattern='^' + str(LANGUAGE) + '$'))
    dp.add_handler(CallbackQueryHandler(donate, pattern='^' + str(DONATIONS) + '$'))

    # This is where tasks are added to the scheduler.
    # The scheduler is built into the telegram library. When I set the same job repeat time, only one job works.
    # This is the minimum viable version, but I will optimize it soon:
    # TODO Create one global job
    updater.job_queue.run_repeating(event_manager, 88, context=EventTypes.CREATEDEVENT, name='createdEvents polling')
    updater.job_queue.run_repeating(event_manager, 92, context=EventTypes.REDEEMEDEVENT, name='redeemedEvents polling')
    updater.job_queue.run_repeating(event_manager, 97, context=EventTypes.FUNDEDEVENT, name='fundedEvents polling')
    updater.job_queue.run_repeating(event_manager, 103, context=EventTypes.SETUPFAILED, name='setupFailed polling')
    updater.job_queue.run_repeating(event_manager, 109, context=EventTypes.LIQUIDATED, name='liquidated polling')
    updater.job_queue.run_repeating(event_manager, 115, context=EventTypes.STARTEDLIQUIDATION, name='started liquidation polling')
    updater.job_queue.run_repeating(event_manager, 119, context=EventTypes.REDEMPTIONREQUESTED, name='redemptionrequested polling')
    updater.job_queue.run_repeating(event_manager, 124, context=EventTypes.GOTREDEMPTIONSIGNATURE, name='got_redemption_signature polling')
    updater.job_queue.run_repeating(event_manager, 131, context=EventTypes.PUBKEYREGISTERED, name='pubkey polling')
    updater.job_queue.run_repeating(event_manager, 137, context=EventTypes.COURTESYCALLED, name='Courtesycalled polling')
    updater.job_queue.run_repeating(event_manager, 142, context=EventTypes.REDEMPTIONREQUESTED, name='Redemptionfee_increased polling')
    updater.job_queue.run_repeating(collateralization, 600, name='collateralization_decreased polling')
    updater.job_queue.run_repeating(check_status, 303, name='node status polling')
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
