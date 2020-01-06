from wxpy import Bot
from wxpy.api.messages import Message
from robot import get_message_helper

from .serializers import WxUserModelSerializer, WxGroupModelSerializer, MessageModelSerializer, WxMpsModelSerializer, \
    ReplyMessage

import pysnooper


class SimpleAction:
    def __init__(self, bot: Bot = None, message: Message = None):
        self.bot = bot
        self.message = message
        self.helper = get_message_helper()

    def get_user(self, user, **kwargs):
        """
        :param user: bot 对象
        :param kwargs: 额外需要保存的参数
        :return: <WxUser>
        """
        serializer = WxUserModelSerializer(context={'user': user})
        return serializer.save(**kwargs)

    def get_group(self, group, update_members=True, **kwargs):
        serializer = WxGroupModelSerializer(context={'group': group})
        return serializer.save(update_members=update_members, **kwargs)

    def get_map(self, maps, **kwargs):
        sserializer = WxMpsModelSerializer(context={'maps': maps})
        return sserializer.save(**kwargs)

    def get_message(self, msg, user, **kwargs):
        serializer = MessageModelSerializer(context={'message': msg, 'user': user})
        return serializer.save(**kwargs)

    def reply_message(self, msg, **kwargs):
        serializer = ReplyMessage(context={'message': msg}, data=kwargs)
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    def reply_text(self, msg, **kwargs):
        text = kwargs.get('text', '')
        return msg.reply_msg(text)

    def reply_image(self, msg, **kwargs):
        helper = self.helper(**kwargs)
        url, save_path = helper.save_send_image()
        return msg.reply_image(save_path)

    def reply_video(self, msg, **kwargs):
        helper = self.helper(**kwargs)
        url, save_path = helper.save_send_video()
        return msg.reply_video(save_path)

    def reply_file(self, msg, **kwargs):
        helper = self.helper(**kwargs)
        url, save_path = helper.save_send_file()
        return msg.reply_file(save_path)

    def get_send_obj(self, **kwargs):
        puid = kwargs.get('puid')
        group = kwargs.get('group', None)
        if group:
            obj = self.bot.groups().search(puid=puid)[0]
        else:
            obj = self.bot.friends().search(puid=puid)[0]
        return obj

    def send_text(self, **kwargs):
        text = kwargs.get('text')
        obj = self.get_send_obj(**kwargs)
        return obj.send(text)

    def send_image(self, **kwargs):
        obj = self.get_send_obj(**kwargs)
        helper = self.helper(**kwargs)
        url, save_path = helper.save_send_file()
        return obj.send_image(save_path)

    def send_file(self, **kwargs):
        obj = self.get_send_obj(**kwargs)
        helper = self.helper(**kwargs)
        url, save_path = helper.save_send_file()
        return obj.send_file(save_path)

    def send_video(self, **kwargs):
        obj = self.get_send_obj(**kwargs)
        helper = self.helper(**kwargs)
        url, save_path = helper.save_send_file()
        return obj.send_video(save_path)
