"""Here are the functions and ConversationHandler for feedback conversation."""
from conversations.conv_utils import WAIT_FEEDBACK, ConversationHandler, main_kb
from conversations.keyboards import back_kb


def feedback(update, context):
    """Function for sending a message with a suggestion to send feedback."""
    update.message.reply_text('Write your feedback:', reply_markup=back_kb)
    return WAIT_FEEDBACK


def send_feedback(update, context):
    """Function for processing feedback."""
    feedback = '<b>#FEEDBACK</b>\n' + update.message.text + '\n' + f'''FROM {update.message.from_user.id}'''
    if username := update.message.from_user.username:
        feedback += f''' @{username}'''

    # TODO SEND TO GOOGLE SHEETS
    context.bot.send_message(text=feedback, chat_id=274980096, parse_mode='HTML')
    update.message.reply_text('Your feedback succesfully added!', reply_markup=main_kb)
    return ConversationHandler.END
