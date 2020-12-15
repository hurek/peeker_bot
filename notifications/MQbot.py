"""Here, the MQBot class is declared, which includes a wrapper over the standard send_message. The bot creates a
queue of messages and we can set limits on messages per second. This allows you not to violate the telegram limits."""
import telegram.bot
from telegram.ext import messagequeue as mq


class MQBot(telegram.bot.Bot):
    def __init__(self, *args, is_queued_def=True, mqueue=None, **kwargs):
        super(MQBot, self).__init__(*args, **kwargs)
        # below 2 attributes should be provided for decorator usage
        self._is_messages_queued_default = is_queued_def
        self._msg_queue = mqueue or mq.MessageQueue()

    def __del__(self):
        try:
            self._msg_queue.stop()
        except:
            pass

    @mq.queuedmessage
    def send_message(self, *args, **kwargs):
        return super(MQBot, self).send_message(*args, **kwargs)