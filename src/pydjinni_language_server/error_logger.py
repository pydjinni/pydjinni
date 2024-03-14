import traceback

from lsprotocol.types import MessageType


def error_logger(func):
    def inner_function(ls, *args, **kwargs):
        try:
            return func(ls, *args, **kwargs)
        except Exception as e:
            ls.show_message_log(traceback.format_exc(), msg_type=MessageType.Error)
    return inner_function
