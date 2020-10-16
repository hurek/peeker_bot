import logging
import telegram
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)
from gql import gql, Client, AIOHTTPTransport
from config import TOKEN
from pony.orm import *
import json
import datetime
from db_tools import *

transport = AIOHTTPTransport(url='https://api.thegraph.com/subgraphs/name/miracle2k/all-the-keeps')
client = Client(transport=transport, fetch_schema_from_transport=True)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

db.generate_mapping(create_tables=True)


def node_stats(): #TODO Move to utils (at the end)
    """Send node stats when the command /stats is issued."""
    query = gql(
        """
		query GetOperators($id: ID!) {
			operators(where: {id: $id}) {
				address
				bonded
				unboundAvailable
				stakedAmount
				totalFaultCount
				involvedInFaultCount
				attributableFaultCount
				totalBeaconRewards
				totalETHRewards
				totalTBTCRewards
				activeKeepCount
				totalKeepCount
			}
		}
		"""
    )
    params = {
        "id": "0xc6325112d6d0a1bb44b3ee2da080a79e99fe4cfe",
    }
    result = client.execute(query, variable_values=params)
    return json.dumps(result, indent=4)


reply_keyboard = [['📝New Address', '📖My Addresses'],
                  ['📨Feedback', '⚙️Settings']]
markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
bot = telegram.Bot(token=TOKEN)

ADD_ADDRESS, USER_ADDRESSES, STORE_ADDRESS, VERIFY_ADDRESS, FEEDBACK = range(5)


def start(update, context):
    update.message.reply_text(text='Hello, my friend! I will notify you about some events!',
                              reply_markup=markup)


def add_address(update, context):
    update.message.reply_text('If you want to cancel, send me /cancel\nPut your address:')
    return STORE_ADDRESS


def store_address(update, context): #TODO add buttons
    update.message.reply_text(
        'If your address correct - put "Correct" or "Resend" for resend your wallet. (there is will be button)')
    return VERIFY_ADDRESS


def success_stored(update, context):
    update.message.reply_text('Address added!')
    return ConversationHandler.END


def resend_address(update, context):
    update.message.reply_text('Resend your address:')
    return STORE_ADDRESS


def incorrect_address(update, context):
    update.message.reply_text('Incorrect address. Please resend address started with 0x')
    return STORE_ADDRESS


def cancel(update, context): #TODO add button
    update.message.reply_text('Bye!')
    return ConversationHandler.END


def get_msg(blockchain, user):
    # this is where you put the main logic wether user should be notified or not
    if user.user_data['sub'] in blockchain:  # TODO Solve how to check users in gql return
        return blockchain[user.user_data['sub']]


def get_time_from_db():  # TODO add import from db
    pass


@db_session
def alerts(context):
    # Send query to subgraph and store results of call in variable blockchain_data
    timestamp = get_time_from_db()  # TODO create function to get the last date from Column
    if timestamp == 0:  # TODO Are we need it?
        timestamp = datetime.now()
    blockchain_data = node_stats()  # TODO Code function for ALERT evernts
    users = []  # TODO Solve how to store and retrieve users/wallets
    for user in users:
        msg = get_msg(blockchain_data, user)
        if msg:
            context.bot.send_message(user.user_id, msg)


def main():
    """Start the bot."""
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    conv_handler = ConversationHandler( #TODO May be move it to handlers.py for importing
        entry_points=[MessageHandler(Filters.regex('^(📝New Address)$'), add_address)],
        states={
            STORE_ADDRESS: [MessageHandler(Filters.regex('^(0x)'), store_address),
                            MessageHandler(Filters.text, incorrect_address)],
            VERIFY_ADDRESS: [MessageHandler(Filters.regex('^(Correct)$'), success_stored),
                             MessageHandler(Filters.regex('^(Resend)$'), resend_address)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dp.add_handler(conv_handler)
    updater.job_queue.run_repeating(alerts, 30, name='polling_blockchain')
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
