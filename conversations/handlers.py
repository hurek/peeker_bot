from telegram.ext import CallbackQueryHandler, CommandHandler, ConversationHandler, Filters, MessageHandler

from conversations.announce import announce, send_announce
from conversations.conv_utils import ANNOUNCE, CHAT_TIMEOUT, STORE_ADDRESS, WAIT_FEEDBACK, cancel, \
    chat_timeout
from conversations.feedback import feedback, send_feedback
from conversations.keyboards import GUIDE_ENTRY, NEW_NAME, RENAME
from conversations.my_adresses import incorrect_name, new_operator_name, rename_operator_address
from conversations.new_address import add_address, incorrect_address, store_address
from conversations.user_guide import guide_entry


class RenameOperatorHandler(ConversationHandler):
    def __init__(self):
        super().__init__(
            entry_points=[CallbackQueryHandler(rename_operator_address, pattern='^' + str(RENAME) + '$')],
            states={
                NEW_NAME: [MessageHandler(Filters.regex('^([a-zA-Z0-9 ]{1,40}$)'), new_operator_name),
                           MessageHandler(Filters.text, incorrect_name)],
                ConversationHandler.TIMEOUT: [MessageHandler(Filters.text | Filters.command, chat_timeout)],
            },
            conversation_timeout=CHAT_TIMEOUT,
            fallbacks=[CommandHandler('cancel', cancel), MessageHandler(Filters.regex('^(⬅️Back)$'), cancel)],
        )


class NewAddressHandler(ConversationHandler):
    def __init__(self):
        super().__init__(
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


class AnnounceHandler(ConversationHandler):
    def __init__(self):
        super().__init__(
            entry_points=[CommandHandler("announce", announce)],
            states={
                ANNOUNCE: [MessageHandler(Filters.regex('^(⬅️Back)$'), cancel),
                           MessageHandler(Filters.text, send_announce)],
                ConversationHandler.TIMEOUT: [MessageHandler(Filters.text | Filters.command, chat_timeout)],
            },
            conversation_timeout=CHAT_TIMEOUT,
            fallbacks=[CommandHandler('cancel', cancel), MessageHandler(Filters.regex('^(⬅️Back)$'), cancel)],
        )


class FeedbackHandler(ConversationHandler):
    def __init__(self):
        super().__init__(
            entry_points=[MessageHandler(Filters.regex('^(📨Feedback)$'), feedback)],
            states={
                WAIT_FEEDBACK: [MessageHandler(Filters.regex('^(⬅️Back)$'), cancel),
                                MessageHandler(Filters.text, send_feedback)],
                ConversationHandler.TIMEOUT: [MessageHandler(Filters.text | Filters.command, chat_timeout)],
            },
            conversation_timeout=CHAT_TIMEOUT,
            fallbacks=[CommandHandler('cancel', cancel), MessageHandler(Filters.regex('^(⬅️Back)$'), cancel)],
        )


#TODO ADD NEW STATES
class UserGuideHandler(ConversationHandler):
    def __init__(self):
        super().__init__(
            entry_points=[CallbackQueryHandler(guide_entry, pattern='^' + str(GUIDE_ENTRY) + '$')],
            states={
                WAIT_FEEDBACK: [MessageHandler(Filters.regex('^(⬅️Back)$'), cancel),
                                MessageHandler(Filters.text, send_feedback)],
                ConversationHandler.TIMEOUT: [MessageHandler(Filters.text | Filters.command, chat_timeout)],
            },
            conversation_timeout=CHAT_TIMEOUT,
            fallbacks=[CommandHandler('cancel', cancel), MessageHandler(Filters.regex('^(⬅️Back)$'), cancel)],
        )


