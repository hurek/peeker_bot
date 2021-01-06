"""Here is the logic for adding a new address operator to the list of addresses tracked by the user."""
from pony.orm import commit, db_session
from telegram.ext import MessageHandler, Filters, CommandHandler

from conversations.conv_utils import *
from configs.db_tools import *
from conversations.keyboards import back_kb
from conversations.short_name import unique_label
from notifications.subgraph_utils import *
import time


@db_session
def store_address(update, context):  # TODO add buttons
    """Function for adding a new address to the list of operators tracked by the user."""
    splitted = update.message.text.split(' ')
    if not check_operator(splitted[0].lower()):
        update.message.reply_text("Oops, I didn't find an operator with this address")
        time.sleep(1)
        return cancel(update, context)
    if not (p := Address.get(operator=splitted[0].lower())):
        p = Address(operator=splitted[0].lower())
    user = User.get(telegram_id=update.message.from_user.id)
    if (ex_name := Label.get(user=user, address=p)):
        if len(splitted) == 1:
            update.message.reply_text(
                f'''This operator address already exists in your watch list with the name <b>{ex_name.label}</b>.''',
                parse_mode='html', reply_markup=main_kb)
        elif len(splitted) > 1:
            ex_name.label = ' '.join(splitted[1:]) #TODO add validation for label
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
    """Function for sending a message with a suggestion to enter a new address."""
    update.message.reply_text(text='Submit the Keep operator Ethereum address and custom name <i>(optional)</i>.'
                                   'You can change the address name in the <b>My Addresses</b> section later.\n\n'
                                   '<code>Example 1:\n0xb8a3ae209d153560993bfd8178e60f09b1c682e8</code>\n'
                                   '<code>Example 2:\n0xb8a3ae209d153560993bfd8178e60f09b1c682e8 WhaleOperator</code>', reply_markup=back_kb, parse_mode='html')
    return STORE_ADDRESS


def incorrect_address(update, context):
    """Function called when an address is entered in the wrong format"""
    update.message.reply_text('Incorrect address. Please send me the Ethereum address.')
    return STORE_ADDRESS

