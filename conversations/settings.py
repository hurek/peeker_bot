"""Functions for the settings conversation."""
from conversations.keyboards import settings_inline_kb, explorers_inline_kb, back_to_settings_inline_kb


def settings(update, context):
    update.message.reply_text('Settings', reply_markup=settings_inline_kb)
    return


def back_to_settings(update, context):
    update.callback_query.edit_message_text('Settings',
                                            inline_message_id=update.callback_query.inline_message_id,
                                            reply_markup=settings_inline_kb)
    return


def explorers(update, context):
    update.callback_query.edit_message_text('Explorers:',
                                            inline_message_id=update.callback_query.inline_message_id,
                                            reply_markup=explorers_inline_kb)
    return


def language_set(update, context):
    update.callback_query.edit_message_text('Sorry, multi-language is under development👨‍💻',
                                            inline_message_id=update.callback_query.inline_message_id,
                                            reply_markup=back_to_settings_inline_kb)
    return


def donate(update, context):
    img = open('donation/qr.png', 'rb')
    text = '🎁 Your donations help us understand that we are moving in the right direction and making a really cool service!\nOur ETH address is' + \
           f'''<a href="https://etherscan.io/address/0xf592eE0E3a20Ddd65882E0fE6bFBB4B465A98Ae4">0xf592eE0E3a20Ddd65882E0fE6bFBB4B465A98Ae4</a>'''
    update.callback_query.message.reply_photo(photo=img, caption=text, parse_mode='html')
    return