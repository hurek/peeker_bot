from telegram.ext import CallbackQueryHandler, CommandHandler, ConversationHandler, Filters, MessageHandler

from conversations.announce import announce, send_announce
from conversations.conv_utils import ANNOUNCE, CHAT_TIMEOUT, STORE_ADDRESS, WAIT_FEEDBACK, cancel, \
    chat_timeout
from conversations.feedback import feedback, send_feedback
from conversations.keyboards import SKIP_TUTORIAL, TUTORIAL_ENTRY, NEW_NAME, RENAME, TUTORIAL_STEP_TWO
from conversations.my_adresses import incorrect_name, new_operator_name, rename_operator_address
from conversations.new_address import add_address, incorrect_address, store_address
from conversations.tutorial import get_started, tutorial_entry, tutorial_step_two


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
            fallbacks=[CommandHandler('cancel', cancel), MessageHandler(Filters.regex('^(⬅️Back)$'), cancel)]
        )


class UserGuideHandler(ConversationHandler):
    def __init__(self):
        super().__init__(
            entry_points=[CallbackQueryHandler(tutorial_entry, pattern='^' + str(TUTORIAL_ENTRY) + '$'),
                          CallbackQueryHandler(get_started, pattern='^' + str(SKIP_TUTORIAL) + '$'),
                          CommandHandler('tutorial', tutorial_entry)],
            states={
                TUTORIAL_STEP_TWO: [CallbackQueryHandler(tutorial_step_two, pattern='^' + str(TUTORIAL_STEP_TWO) + '$')],
                ConversationHandler.TIMEOUT: [MessageHandler(Filters.text | Filters.command, chat_timeout)],
            },
            conversation_timeout=CHAT_TIMEOUT,
            fallbacks=[CallbackQueryHandler(get_started, pattern='^' + str(SKIP_TUTORIAL) + '$')]
        )


