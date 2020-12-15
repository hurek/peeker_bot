"""Here are some functions for conversations."""
from telegram.ext import ConversationHandler
from conversations.keyboards import *
from notifications.event_types import EventTypes

ADD_ADDRESS, \
USER_ADDRESSES, \
STORE_ADDRESS, \
VERIFY_ADDRESS, \
FEEDBACK, \
WAIT_FEEDBACK, \
FEEDBACK_SEND, \
MY_ADDRESSES, \
ACTIONS = range(9)

CHAT_TIMEOUT = 60


def cancel(update, context):  # TODO add button
    """Function to cancel current conversation."""
    update.message.reply_text(text="Let's start over!", reply_markup=main_kb)
    return ConversationHandler.END


def chat_timeout(update, context):
    """Function to end the conversation if a timeout occurs."""
    update.message.reply_text('Sorry, there was a timeout. Try again.', reply_markup=main_kb)
    return ConversationHandler.END


def subscribe_event_dict():
    """A function that returns a dictionary with notification types and their values."""
    dictionary = {
        str(NODESTATUS): {'type': EventTypes.NODESTATUS.value},
        str(CREATED): {'type': EventTypes.CREATEDEVENT.value},
        str(REDEEMED): {'type': EventTypes.REDEEMEDEVENT.value},
        str(FUNDED): {'type': EventTypes.FUNDEDEVENT.value},
        str(SETUPFAILED): {'type': EventTypes.SETUPFAILED.value},
        str(LIQUIDATED): {'type': EventTypes.LIQUIDATED.value},
        str(STARTEDLIQUIDATION): {'type': EventTypes.STARTEDLIQUIDATION.value},
        str(REDEMPTIONREQUESTED): {'type': EventTypes.REDEMPTIONREQUESTED.value},
        str(GOTREDEMPTIONSIGNATURE): {'type': EventTypes.GOTREDEMPTIONSIGNATURE.value},
        str(PUBKEYREGISTERED): {'type': EventTypes.PUBKEYREGISTERED.value},
        str(CRATIODECREASED): {'type': EventTypes.CRATIODECREASED.value},
        str(COURTESYCALLED): {'type': EventTypes.COURTESYCALLED.value},
        str(REDEMPTIONFEEINCREASED): {'type': EventTypes.REDEMPTIONFEEINCREASED.value}
    }
    return dictionary
