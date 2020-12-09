from telegram.ext import CallbackQueryHandler, MessageHandler, CommandHandler, Filters

from conv.conv_utils import *
from db_tools import *
from notifications.subgraph_utils import *
import jsonpickle
from conv.keyboards import *
import re


@db_session
def my_addresses(update, context):
    user = User.get(telegram_id=update.message.from_user.id)
    if not user.labels:
        update.message.reply_text("You don't have any saved addresses yet. Click <b>New Address</b> to add your first "
                                  "address.", parse_mode='html')
    for label in user.labels:
        link = f'''<a href="https://allthekeeps.com/operator/{label.address.operator}">{label.address.operator}</a>'''
        msg = f'''<b>{label.label}</b>\n{link}\n'''
        result = jsonpickle.decode(node_stats(label.address.operator))
        stats = node_stats_parser(result)
        update.message.reply_text(msg + stats + '\n', reply_markup=first_operator_inline_kb, parse_mode='html')
        commit()
    return


@db_session
def inline_configure(update, context):
    msg = update.callback_query.message.text_html
    operator = re.search('(0x[a-fA-F0-9]{40})', msg).group(0)
    user = User.get(telegram_id=update.callback_query.from_user.id)
    address = Address.get(operator=operator)
    update.callback_query.edit_message_reply_markup(reply_markup=change_inline_kb(user, address),
                                                    inline_message_id=update.callback_query.inline_message_id)
    return


def change_inline_kb(user, address):
    buttons = []
    for key, value in keyboard_dict.items():
        if not Tracking.get(user=user, operator=address, type=value['value']):
            buttons.append([InlineKeyboardButton(text="💤" + value['name'], callback_data=key)])
        else:
            buttons.append([InlineKeyboardButton(text="✅" + value['name'], callback_data=key)])
    buttons.append([InlineKeyboardButton("⬅️Back", callback_data=str(BACK))])
    kb = InlineKeyboardMarkup(buttons)
    return kb


def inline_back(update, context):
    update.callback_query.edit_message_reply_markup(reply_markup=first_operator_inline_kb, inline_message_id=update.callback_query.inline_message_id)
    return


def inline_close(update, context):
    update.callback_query.message.delete()
    return


@db_session
def rename_operator_address(update, context):
    context.user_data.clear()
    user = User.get(telegram_id=update.callback_query.from_user.id)
    msg = update.callback_query.message.text_html
    operator = re.search('(0x[a-fA-F0-9]{40})', msg).group(0)
    address = Address.get(operator=operator)
    label = Label.get(address=address, user=user)
    context.user_data["address"] = operator
    rename_message = 'Enter new name for ' + f'''<a href="https://allthekeeps.com/operator/{operator}">{label.label}</a>\nThe name must be up to 40 characters long and contain any English uppercase and lowercase letters, numbers and spaces.'''
    update.callback_query.message.reply_text(rename_message, parse_mode='html')
    return NEW_NAME


@db_session
def new_operator_name(update, context):
    address = Address.get(operator=context.user_data['address'])
    user = User.get(telegram_id=update.message.from_user.id)
    new_name = update.message.text
    label = Label.get(user=user, address=address)
    label.label = new_name
    commit()
    context.user_data.clear()
    succesful_renamed = 'Operator address '\
                        + f'''<a href="https://allthekeeps.com/operator/{address.operator}">{address.operator}</a>'''\
                        + ' named as ' + '<b>' + new_name + '</b>'
    update.message.reply_text(succesful_renamed, parse_mode='html')
    return ConversationHandler.END


def incorrect_name(update, context):
    update.message.reply_text('Invalid name. Please enter 1-40 symbols length name.')
    return NEW_NAME


@db_session
def delete_user_address(update, context):
    user = User.get(telegram_id=update.callback_query.from_user.id)
    msg = update.callback_query.message.text_html
    operator = re.search('(0x[a-fA-F0-9]{40})', msg).group(0)
    address = Address.get(operator=operator)
    label = Label.get(user=user, address=address)
    name = label.label
    label.delete()
    if trackings := select(t for t in Tracking if (t.operator == address and t.user == user)):
        for i in trackings:
            i.delete()
    commit()
    msg = 'Operator address deleted. Details:\n' + '<b>Name: ' + name + '</b>\n' + '<i>' + operator + '</i>'
    update.callback_query.edit_message_text(text=msg,
                                            inline_message_id=update.callback_query.inline_message_id, parse_mode='html')
    return


@db_session
def subscribe_event(update, context):
    events = subscribe_event_dict()
    current_event = events[update.callback_query.data]
    msg = update.callback_query.message.text_html
    operator = re.search('(0x[a-fA-F0-9]{40})', msg).group(0)
    user = User.get(telegram_id=update.callback_query.from_user.id)
    address = Address.get(operator=operator)
    if not Tracking.get(user=user, operator=address, type=current_event['type']):
        tracking = Tracking(user=user, operator=address, type=current_event['type'])
    else:
        tracking = Tracking.get(user=user, operator=address, type=current_event['type'])
        tracking.delete()
    commit()
    update.callback_query.edit_message_reply_markup(inline_message_id=update.callback_query.inline_message_id,
                                            reply_markup=change_inline_kb(user, address))
    return


# TODO move to handlers.py
rename_operator_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(rename_operator_address, pattern='^' + str(RENAME) + '$')],
    states={
        NEW_NAME: [MessageHandler(Filters.regex('^([a-zA-Z0-9 ]{1,40}$)'), new_operator_name),
                        MessageHandler(Filters.text, incorrect_name)],
        ConversationHandler.TIMEOUT: [MessageHandler(Filters.text | Filters.command, chat_timeout)],
    },
    conversation_timeout=CHAT_TIMEOUT,
    fallbacks=[CommandHandler('cancel', cancel), MessageHandler(Filters.regex('^(⬅️Back)$'), cancel)],
)