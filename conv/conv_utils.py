from telegram.ext import ConversationHandler
from conv.keyboards import *
from notifications.types import *

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
    update.message.reply_text(text="Let's start over!", reply_markup=main_kb)
    return ConversationHandler.END


def chat_timeout(update, context):
    update.message.reply_text('Sorry, there was a timeout. Try again.', reply_markup=main_kb)
    return ConversationHandler.END


def subscribe_event_dict():
    dictionary = {
        str(CREATED): {
            'type': EventTypes.CREATEDEVENT.value,
            'text': 'New Deposit: '
        },
        str(REDEEMED): {
            'type': EventTypes.REDEEMEDEVENT.value,
            'text': 'Deposit Redeemed: '
        },
        str(FUNDED): {
            'type': EventTypes.FUNDEDEVENT.value,
            'text': 'Deposit Funded: '
        },
        str(SETUPFAILED): {
            'type': EventTypes.SETUPFAILED.value,
            'text': 'Setup Failed: '
        },
        str(LIQUIDATED): {
            'type': EventTypes.LIQUIDATED.value,
            'text': 'Deposit Liquidated: '
        },
        str(STARTEDLIQUIDATION): {
            'type': EventTypes.STARTEDLIQUIDATION.value,
            'text': 'Liquidation Started: '
        },
        str(REDEMPTIONREQUESTED): {
            'type': EventTypes.REDEMPTIONREQUESTED.value,
            'text': 'Redemption Requested: '
        },
        str(GOTREDEMPTIONSIGNATURE): {
            'type': EventTypes.GOTREDEMPTIONSIGNATURE.value,
            'text': 'Redemption Started: '
        },
        str(PUBKEYREGISTERED): {
            'type': EventTypes.PUBKEYREGISTERED.value,
            'text': 'Pubkey Registered: '
        }
        ,
        str(COURTESYCALLED): {
            'type': EventTypes.COURTESYCALLED.value,
            'text': 'Courtesy Call: '
        }
        ,
        str(REDEMPTIONFEEINCREASED): {
            'type': EventTypes.REDEMPTIONFEEINCREASED.value,
            'text': 'Redemption Fee Increased: '
        }
    }
    return dictionary