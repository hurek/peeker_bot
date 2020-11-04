from telegram.ext import MessageHandler, Filters, CommandHandler

from conv.conv_utils import *
from db_tools import *
from conv.random_aaa import unique_label
from notifications.subgraph_utils import *
import time


@db_session
def store_address(update, context):  # TODO add buttons
    splitted = update.message.text.split(' ')
    if not check_operator(splitted[0]):
        update.message.reply_text("Oops, I didn't find an operator with this address")
        time.sleep(1)
        return cancel(update, context)
    if not (p := Address.get(operator=splitted[0])):
        p = Address(operator=splitted[0])
    user = User.get(telegram_id=update.message.from_user.id)
    if (ex_name := Label.get(user=user, address=p)):
        if len(splitted) == 1:
            update.message.reply_text(
                f'''This operator address already exists in your watch list with the name <b>{ex_name.label}</b>.''',
                parse_mode='html', reply_markup=main_kb)
        elif len(splitted) > 1:
            ex_name.label = ' '.join(splitted[1:])
            update.message.reply_text(text="The operator address name was successfully updated!", reply_markup=main_kb)
        commit()
        return ConversationHandler.END
    if len(splitted) == 1:
        name = Label(user=user, address=p)
        name.label = unique_label(p.operator)
    elif len(splitted) > 1:
        name = Label(user=user, address=p, label=' '.join(splitted[1:]))
    commit()
    update.message.reply_text(text=f'''Address succesfully added with name <b>{name.label}</b>.''', parse_mode='html',
                              reply_markup=main_kb)
    return ConversationHandler.END


def add_address(update, context):
    update.message.reply_text(text='Submit the Keep operator Ethereum address (format: 0x00...). You can change the address name in the address settings later.', reply_markup=back_kb)
    return STORE_ADDRESS


def incorrect_address(update, context):
    update.message.reply_text('Incorrect address. Please send me the Ethereum address.')
    return STORE_ADDRESS


new_address_handler = ConversationHandler(  # TODO May be move it to handlers.py for importing
    entry_points=[MessageHandler(Filters.regex('^(📝New Address)$'), add_address)],
    states={
        STORE_ADDRESS: [MessageHandler(Filters.regex('^(0x[a-fA-F0-9]{40})'), store_address),
                        MessageHandler(Filters.regex('^(⬅️Back)$'), cancel),
                        MessageHandler(Filters.text, incorrect_address)],
        ConversationHandler.TIMEOUT: [MessageHandler(Filters.text | Filters.command, chat_timeout)],
    },
    conversation_timeout=CHAT_TIMEOUT,
    fallbacks=[CommandHandler('cancel', cancel), MessageHandler(Filters.regex('^(⬅️Back)$'), cancel)],
)
