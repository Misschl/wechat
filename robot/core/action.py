from wxpy import Bot
from wxpy.api.messages import Message

from .serializers import WxUserModelSerializer, WxGroupModelSerializer, MessageModelSerializer, WxMpsModelSerializer


class SimpleAction:
    def __init__(self, bot: Bot = None, message: Message = None):
        self.bot = bot
        self.message = message

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

    def get_message(self, msg, **kwargs):
        serializer = MessageModelSerializer(context={'message': msg})
        return serializer.save(**kwargs)
