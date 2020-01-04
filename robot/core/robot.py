from django.conf import settings

from robot import models
from wxpy import Bot
from wxpy.api.messages import MessageConfig

from .security import create_signature
from .action import SimpleAction
from robot import get_message_helper

from threading import Thread
import os
import time

UPDATE = False


class Quene(dict):

    def update(self, item, **kwargs) -> None:
        global UPDATE
        if UPDATE is False:
            Thread(target=self.listenning_robot).start()
            UPDATE = True
        return super().update(item, **kwargs)

    def listenning_robot(self):
        for bot in self.values():
            print(bot.bot.self.name, bot.bot.alive)
        time.sleep(1)
        return self.listenning_robot()


quene = Quene()


class Robot:

    def __init__(self, bot: Bot, app: models.AppModel):
        self.bot = bot
        self.app = app
        # 存储pkl
        pkl_path = app.puid_pkl
        bot.enable_puid(pkl_path)
        self._user = bot.self
        self.message_helper = get_message_helper()
        self.action = SimpleAction(bot=self.bot)
        self.get_current_user()
        self.register()

    def get_current_user(self):
        """记录当前的用户"""
        # 获取头像
        avatar = self.message_helper().get_avatar(self._user)
        # 更新或创建信息
        user = self.action.get_user(user=self._user, avatar=avatar, is_friend=True)
        user.owner = user
        user.save()
        bind_user = self.app.bind_user
        if bind_user is None:
            # 绑定app用户
            self.app.bind_user = user
            self.app.save()
        setattr(self, 'user', user)
        return user

    def register(self, chats=None, msg_types=None, except_self=True, run_async=True, enabled=True):
        func = self.forward
        self.bot.registered.append(
            MessageConfig(bot=self.bot, func=func, chats=chats, msg_types=msg_types, except_self=except_self,
                          run_async=run_async, enabled=enabled))

    def forward(self, msg):
        pass

    def get_forward_url(self):
        timestamp = f'{int(time.time() * 1000)}'
        data = [self.app.app_id, self.app.token, timestamp]
        signature = create_signature(data)
        forward_url = f'{self.app.forward_url}?timestamp={timestamp}&signature={signature}'
        return forward_url
