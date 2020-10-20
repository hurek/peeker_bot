import logging
import telegram
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)

from config import TOKEN
from pony.orm import *
import json
import datetime
from db_tools import *
import jsonpickle
from subgraph_utils import *


# Logger settings
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


# Generate mapping and if tables not exists - create them
db.generate_mapping(create_tables=True)


# Main keyboard settings
reply_keyboard = [['📝New Address', '📖My Addresses'],
                  ['📨Feedback', '⚙️Settings']]
markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
bot = telegram.Bot(token=TOKEN)


# Conversation settings
CHAT_TIMEOUT = 60
ADD_ADDRESS, USER_ADDRESSES, STORE_ADDRESS, VERIFY_ADDRESS, FEEDBACK, CORRECT_ADDRESS, REENTER_ADDRESS, CANCEL = range(
    8)


# /start function
def start(update, context):
    with db_session:
        if not select(p.telegram_id for p in User if p.telegram_id == update.message.chat_id):
            p = User(telegram_id=update.message.from_user.id, username=update.message.from_user.username)
            commit()
    update.message.reply_text(text='Hello, my friend! I will notify you about some events!',
                              reply_markup=markup)



def add_address(update, context):
    update.message.reply_text('If you want to cancel, send me /cancel\nPut your address:')
    return STORE_ADDRESS


@db_session
def store_address(update, context):  # TODO add buttons
    if not select(p.operator for p in Address if p.operator == update.message.text):
        p = Address(operator=update.message.text)
        commit()
    else:
        p = Address.get(operator=update.message.text)
        user = User.get(telegram_id=update.message.from_user.id)
        user.addresses = p
        commit()
    # kb = [['✅Confirm', '🔁Re-enter'], ['cancel']] #TODO its just backup of ReplyKeyboardButtons
    # submit_kb = ReplyKeyboardMarkup(kb, resize_keyboard=True)
    kb = [                                                                  # TODO fix InlineKeyboardButton error
        [
            InlineKeyboardButton("Confirm", callback_data=str(CORRECT_ADDRESS)),
            InlineKeyboardButton("Re-enter", callback_data=str(REENTER_ADDRESS)),
            InlineKeyboardButton("Cancel", callback_date=str(CANCEL)),
        ]
    ]
    submit_kb = InlineKeyboardMarkup(kb)
    update.message.reply_text(f"""Your address:\n{update.message.text}\nIs it ok?""", reply_markup=submit_kb)
    return VERIFY_ADDRESS


def success_stored(update, context):
    update.message.reply_text('Address added!', reply_markup=markup)
    return ConversationHandler.END


def resend_address(update, context):
    update.message.reply_text('Resend your address:')
    return STORE_ADDRESS


def incorrect_address(update, context):
    update.message.reply_text('Incorrect address. Please resend address started with 0x')
    return STORE_ADDRESS


def cancel(update, context):  # TODO add button
    update.message.reply_text('Bye!', reply_markup=markup)
    return ConversationHandler.END


def chat_timeout(update, context):
    update.message.reply_text('Sorry, there was a timeout. Try again.', reply_markup=markup)
    return ConversationHandler.END


def get_msg(blockchain, user):
    # this is where you put the main logic wether user should be notified or not
    pass    # TODO make notification function with db


def get_time_from_db():  # TODO Check for erros (may be I'm stupid lol)
    if not select(date for date in ScheduleTiming).order_by(lambda date: desc(date.id)).first():
        date = ScheduleTiming(alerts=int(datetime.timestamp(datetime.now())))
        commit()
    else:
        date = select(date for date in ScheduleTiming).order_by(lambda date: desc(date.id)).first()
        current = ScheduleTiming(alerts=int(datetime.timestamp(datetime.now())))
        commit()
    return date.alerts


@db_session
def created_events(context):
    #timestamp = get_time_from_db() #TODO uncomment when finish parser. I think it works fine
    timestamp = 1602622798
    blockchain_data = jsonpickle.decode(created_events_query(timestamp))
    events_data = created_events_parser(blockchain_data)  # TODO Solve how to store and retrieve users/wallets
    for event in events_data:
        print('NEW EVENT:')
        for address in event['members']:
            print(f"""Your operator {address} got selected for a new deposit: More informations: {event['link']}""")
        print('')
    # for user in users: #TODO need to code function for check subscribers for event
    #     msg = get_msg(blockchain_data, user)
    #     if msg:
    #         context.bot.send_message(user.user_id, msg)


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    conv_handler = ConversationHandler(  # TODO May be move it to handlers.py for importing
        entry_points=[MessageHandler(Filters.regex('^(📝New Address)$'), add_address)],
        states={
            STORE_ADDRESS: [MessageHandler(Filters.regex('^(0x)'), store_address),
                            MessageHandler(Filters.text, incorrect_address)],
            # VERIFY_ADDRESS: [MessageHandler(Filters.regex('^(✅Confirm)$'), success_stored), #TODO its just backup of ReplyKeyboard
            #                 MessageHandler(Filters.regex('^(🔁Re-enter)$'), resend_address)],
            VERIFY_ADDRESS: [CallbackQueryHandler(success_stored, pattern='^' + str(CORRECT_ADDRESS) + '$'), #TODO fix InlineKeyboard errors
                             CallbackQueryHandler(resend_address, pattern='^' + str(REENTER_ADDRESS) + '$'),
                             CallbackQueryHandler(resend_address, pattern='^' + str(CANCEL) + '$')
                             ],
            ConversationHandler.TIMEOUT: [MessageHandler(Filters.text | Filters.command, chat_timeout)],
        },

        conversation_timeout=CHAT_TIMEOUT,
        fallbacks=[CommandHandler('cancel', cancel), MessageHandler(Filters.regex('^(cancel)$'), cancel)],
    )
    dp.add_handler(conv_handler)


    updater.job_queue.run_repeating(created_events, 5, name='polling_blockchain') #TODO change 5 to 30 or 60 sec
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
