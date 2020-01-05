from django.utils.module_loading import import_string
from django.conf import settings

DEFAULT_MESSAGE_HELPER = getattr(settings, 'DEFAULT_MESSAGE_HELPER', 'robot.core.file.FileHandle')

DEFAULT_ACTION = getattr(settings, 'DEFAULT_ACTION_CLASS', 'robot.core.action.FileHandle')


def get_message_helper():
    return import_string(DEFAULT_MESSAGE_HELPER)
