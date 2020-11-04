import logging
from telegram.ext import Updater
from config import TOKEN
from telegram.utils.request import Request
from conv.my_adresses import *
from conv.new_address import *
from conv.feedback import *
from conv.settings import *
from polog.flog import flog
from notifications.MQbot import *
from notifications.event_manager import *

# Logger settings
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Generate mapping and if tables not exists - create them
db.generate_mapping(create_tables=True)


@db_session
def start(update, context):
    if not (p := User.get(telegram_id=update.message.chat_id)):
        p = User(telegram_id=update.message.from_user.id, username=update.message.from_user.username)
        commit()
    update.message.reply_text(text='Hello 👋 I am a beta release of Peeker bot. For this reason if you have any suggestions or ideas you may contact to my creator👨‍💻.\n\nMy specific feature is delicate adjustment ⚙️ of notifications for every operator address. I already know how to send several types of notifications, but in the very near future I will learn how to do a lot more!',
                              reply_markup=main_kb)


@flog
def main():
    q = mq.MessageQueue(all_burst_limit=20, all_time_limit_ms=1500)
    request = Request(con_pool_size=8)
    peeker_bot = MQBot(TOKEN, request=request, mqueue=q)
    updater = Updater(bot=peeker_bot, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(new_address_handler)
    dp.add_handler(feedback_handler)

    dp.add_handler(MessageHandler(Filters.regex('^(📖My Addresses)$'), my_addresses))
    dp.add_handler(CallbackQueryHandler(inline_configure, pattern='^' + str(CONFIGURE) + '$'))
    dp.add_handler(CallbackQueryHandler(inline_close, pattern='^' + str(CLOSE) + '$'))
    dp.add_handler(CallbackQueryHandler(inline_back, pattern='^' + str(BACK) + '$'))

    dp.add_handler(CallbackQueryHandler(subscribe_event, pattern='^' + str(CREATED) + '$'))
    dp.add_handler(CallbackQueryHandler(subscribe_event, pattern='^' + str(REDEEMED) + '$'))
    dp.add_handler(CallbackQueryHandler(subscribe_event, pattern='^' + str(FUNDED) + '$'))
    dp.add_handler(CallbackQueryHandler(subscribe_event, pattern='^' + str(SETUPFAILED) + '$'))
    dp.add_handler(CallbackQueryHandler(subscribe_event, pattern='^' + str(LIQUIDATED) + '$'))
    dp.add_handler(CallbackQueryHandler(subscribe_event, pattern='^' + str(STARTEDLIQUIDATION) + '$'))
    dp.add_handler(CallbackQueryHandler(subscribe_event, pattern='^' + str(REDEMPTIONREQUESTED) + '$'))
    dp.add_handler(CallbackQueryHandler(subscribe_event, pattern='^' + str(GOTREDEMPTIONSIGNATURE) + '$'))
    dp.add_handler(CallbackQueryHandler(subscribe_event, pattern='^' + str(PUBKEYREGISTERED) + '$'))
    dp.add_handler(CallbackQueryHandler(subscribe_event, pattern='^' + str(COURTESYCALLED) + '$'))
    dp.add_handler(CallbackQueryHandler(subscribe_event, pattern='^' + str(REDEMPTIONFEEINCREASED) + '$'))
    dp.add_handler(CallbackQueryHandler(delete_user_address, pattern='^' + str(DELETE) + '$'))
    dp.add_handler(rename_operator_handler)

    dp.add_handler(MessageHandler(Filters.regex('^(⚙️Settings)$'), settings))
    dp.add_handler(CallbackQueryHandler(explorers, pattern='^' + str(EXPLORER) + '$'))
    dp.add_handler(CallbackQueryHandler(language_set, pattern='^' + str(LANGUAGE) + '$'))
    dp.add_handler(CallbackQueryHandler(donate, pattern='^' + str(DONATIONS) + '$'))

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
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
