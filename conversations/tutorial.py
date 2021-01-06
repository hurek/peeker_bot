from telegram.ext import ConversationHandler

from conversations.keyboards import SKIP_TUTORIAL, TUTORIAL_STEP_TWO, main_kb, tutorial_end_kb, tutorial_step_two_kb


def tutorial_entry(update, context):
    if not update.message.text:
        update.callback_query.edit_message_text(
            "<b>Step 1: Add an operator address</b>\n\n"
            "1. Click the <b>New Address</b> button to add a new address for monitoring.\n"
            "2. Enter the ETH address of your operator, as well as set it a custom "
            "name <i>(Optional. You can change the name later in the My Addresses section</i>).\n\n "
            "<code>Example:\n0xb8a3ae209d153560993bfd8178e60f09b1c682e8 WhaleOperator</code>",
            parse_mode='HTML', reply_markup=tutorial_step_two_kb
        )
    else:
        update.message.reply_text(
            "<b>Step 1: Add an operator address</b>\n\n"
            "1. Click the <b>New Address</b> button to add a new address for monitoring.\n"
            "2. Enter the ETH address of your operator, as well as set it a custom "
            "name <i>(Optional. You can change the name later in the My Addresses section</i>).\n\n "
            "<code>Example:\n0xb8a3ae209d153560993bfd8178e60f09b1c682e8 WhaleOperator</code>",
            parse_mode='HTML', reply_markup=tutorial_step_two_kb
        )
    return TUTORIAL_STEP_TWO


def get_started(update, context):
    update.callback_query.message.delete()
    update.callback_query.message.reply_text("Well, let's get started!", reply_markup=main_kb)
    return ConversationHandler.END


def tutorial_step_two(update, context):
    update.callback_query.edit_message_text(
        "<b>Step 2: Customize the addresses settings.</b>\n\n"
        "1. Click the <b>My Addresses</b> button to view the list of added addresses.\n"
        "2. Click the <b>Rename</b> button to add/change custom name of address.\n"
        "3. Click the <b>Delete</b> button to delete address from your watchlist.\n"
        "4. Click the <b>Notifications</b> button customize notifications for this address.\n\n"
        "<i>If you still have questions, write in the discord rdfbbx#6437</i>",
        parse_mode='HTML', reply_markup=tutorial_end_kb
    )
    return SKIP_TUTORIAL