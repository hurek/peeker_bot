from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from config import TOKEN
import requests
import json


def start(update, context):
	"""Send a message when the command /start is issued."""
	update.message.reply_text('Hello, my friend! I will notify you about some events!')


def help_command(update, context):
	"""Send a message when the command /help is issued."""
	update.message.reply_text('I have not "Help" functions yet=(')


def stats(update, context):
	"""Send a result of query when the command /stats is issued."""
	query = """query {
  tbtcdepositTokens(first: 5) {
    id
    deposit {
      id
    }
    tokenID
    owner
  }
  createdEvents(first: 5) {
    id
    submitter
    transactionHash
    timestamp
  }
}"""
	url = 'https://api.thegraph.com/subgraphs/name/miracle2k/all-the-keeps'
	r = requests.post(url, json={'query': query})
	print(r.status_code)
	print(json.dumps(r.json(), indent=4))
	update.message.reply_text(json.dumps(r.json(), indent=4))


# def echo(update, context):
#     """Echo the user message."""
#     update.message.reply_text(update.message.text)


def main():
	"""Start the bot."""
	# Create the Updater and pass it your bot's token.
	# Make sure to set use_context=True to use the new context based callbacks
	# Post version 12 this will no longer be necessary
	updater = Updater(TOKEN, use_context=True)

	# Get the dispatcher to register handlers
	dp = updater.dispatcher

	# on different commands - answer in Telegram
	dp.add_handler(CommandHandler("start", start))
	dp.add_handler(CommandHandler("help", help_command))
	dp.add_handler(CommandHandler("stats", stats))

	# on noncommand i.e message - echo the message on Telegram
	# dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

	# Start the Bot
	updater.start_polling()

	# Run the bot until you press Ctrl-C or the process receives SIGINT,
	# SIGTERM or SIGABRT. This should be used most of the time, since
	# start_polling() is non-blocking and will stop the bot gracefully.
	updater.idle()


if __name__ == '__main__':
	main()
