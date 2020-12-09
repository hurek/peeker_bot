from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from notifications.types import EventTypes

DELETE, CONFIGURE, CLOSE, \
RENAME, NEW_NAME, CREATED, \
REDEEMED, EXPLORER, LANGUAGE, \
DONATIONS, FUNDED, BACK, \
SETUPFAILED, LIQUIDATED, STARTEDLIQUIDATION, \
REDEMPTIONREQUESTED, GOTREDEMPTIONSIGNATURE, \
PUBKEYREGISTERED, COURTESYCALLED, REDEMPTIONFEEINCREASED = range(20)

main_keyboard = [['📝New Address', '📖My Addresses'],
                 ['📨Feedback', '⚙️Settings']]
main_kb = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)

back_keyboard = [['⬅️Back']]
back_kb = ReplyKeyboardMarkup(back_keyboard, resize_keyboard=True)

keyboard_dict = {
    str(CREATED): {'value': EventTypes.CREATEDEVENT.value, 'name': 'New Deposit'},
    str(REDEEMED): {'value': EventTypes.REDEEMEDEVENT.value, 'name': 'Deposit Redeemed'},
    str(FUNDED): {'value': EventTypes.FUNDEDEVENT.value, 'name': 'Deposit Funded'},
    str(SETUPFAILED): {'value': EventTypes.SETUPFAILED.value, 'name': 'Setup Failed'},
    str(LIQUIDATED): {'value': EventTypes.LIQUIDATED.value, 'name': 'Deposit Liquidated'},
    str(STARTEDLIQUIDATION): {'value': EventTypes.STARTEDLIQUIDATION.value, 'name': 'Liquidation Started'},
    str(REDEMPTIONREQUESTED): {'value': EventTypes.REDEMPTIONREQUESTED.value, 'name': 'Redemption Requested'},
    str(GOTREDEMPTIONSIGNATURE): {'value': EventTypes.GOTREDEMPTIONSIGNATURE.value, 'name': 'Redemption Signature'},
    str(PUBKEYREGISTERED): {'value': EventTypes.PUBKEYREGISTERED.value, 'name': 'Pubkey Registered'},
    str(COURTESYCALLED): {'value': EventTypes.COURTESYCALLED.value, 'name': 'Courtesy Call'},
    str(REDEMPTIONFEEINCREASED): {'value': EventTypes.REDEMPTIONFEEINCREASED.value, 'name': 'Redemption Fee Increased'}
}

first_inline_keyboard = [
    [
        InlineKeyboardButton("📝Rename", callback_data=str(RENAME)),
        InlineKeyboardButton("🗑Delete", callback_data=str(DELETE))
    ],
    [InlineKeyboardButton("🔧Notifications", callback_data=str(CONFIGURE))]
]
first_operator_inline_kb = InlineKeyboardMarkup(first_inline_keyboard)

settings_inline_keyboard = [
    [InlineKeyboardButton("🌐Explorers", callback_data=str(EXPLORER)),
     InlineKeyboardButton("🇺🇸Language", callback_data=str(LANGUAGE))
     ],
    [InlineKeyboardButton("🎁Donate", callback_data=str(DONATIONS))],
    [InlineKeyboardButton("❌Close", callback_data=str(CLOSE))]
]
settings_inline_kb = InlineKeyboardMarkup(settings_inline_keyboard)

explorers_inline_keyboard = [
    [InlineKeyboardButton("KeepScan.com", url='https://keepscan.com/')],
    [InlineKeyboardButton("AllTheKeeps.com", url='https://allthekeeps.com/deposits')],
    [InlineKeyboardButton("KeepStats.org", url='https://keepstats.org/')],
    [InlineKeyboardButton("KeepExplorer.com", url='https://keepexplorer.com/')],
    [InlineKeyboardButton("❌Close", callback_data=str(CLOSE))]
]
explorers_inline_kb = InlineKeyboardMarkup(explorers_inline_keyboard)

back_to_settings_inline_keyboard = [
    [InlineKeyboardButton("❌Close", callback_data=str(CLOSE))]
]
back_to_settings_inline_kb = InlineKeyboardMarkup(back_to_settings_inline_keyboard)
