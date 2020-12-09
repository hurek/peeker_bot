from telegram.ext import MessageHandler, Filters, CommandHandler

from conv.conv_utils import *


def feedback(update, context):
    update.message.reply_text('Write your feedback:', reply_markup=back_kb)
    return WAIT_FEEDBACK


def send_feedback(update, context):

    feedback = '<b>#FEEDBACK</b>\n' + update.message.text + '\n' + f'''FROM {update.message.from_user.id}'''
    if (username := update.message.from_user.username):
        feedback += f''' @{username}'''

    # TODO SEND TO GOOGLE SHEETS
    context.bot.send_message(text=feedback, chat_id=274980096, parse_mode='HTML')
    update.message.reply_text('Your feedback succesfully added!', reply_markup=main_kb)
    return ConversationHandler.END


feedback_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.regex('^(📨Feedback)$'), feedback)],
    states={
        WAIT_FEEDBACK: [MessageHandler(Filters.regex('^(⬅️Back)$'), cancel),
                        MessageHandler(Filters.text, send_feedback)],
        ConversationHandler.TIMEOUT: [MessageHandler(Filters.text | Filters.command, chat_timeout)],
    },
    conversation_timeout=CHAT_TIMEOUT,
    fallbacks=[CommandHandler('cancel', cancel), MessageHandler(Filters.regex('^(⬅️Back)$'), cancel)],
)
