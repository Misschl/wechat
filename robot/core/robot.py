from django.conf import settings

from robot import models
from wxpy import Bot
from wxpy.api.messages import MessageConfig

from .security import create_signature
from .action import SimpleAction
from robot import get_message_helper
from utils.etc import show_spend_time

from threading import Thread
from concurrent.futures import ThreadPoolExecutor
import os
import time, logging

DEFAULT_UPDATE_FREQUENCY = getattr(settings, 'UPDATE_FREQUENCY', 60 * 60 * 2)


class Quene(dict):
    UPDATE = False
    action = SimpleAction()
    helper = get_message_helper()

    def update(self, item, **kwargs) -> None:
        if self.UPDATE is False:
            Thread(target=self.listening_robot).start()
            self.UPDATE = True
        return super().update(item, **kwargs)

    def listening_robot(self):
        for bot in self.values():
            self.update_friend_and_group(bot)
        time.sleep(DEFAULT_UPDATE_FREQUENCY)
        return self.listening_robot()

    @show_spend_time
    def update_friend_and_group(self, bot):
        update_group = Thread(target=self.update_groups, args=(bot,))
        update_friend = Thread(target=self.update_friends, args=(bot,))
        update_group.start()
        update_friend.start()
        update_group.join()
        update_friend.join()

    def update_groups(self, bot):
        groups = bot.bot.groups(update=True)
        owner = bot.user
        max_workers = self.get_max_workers(groups)
        with ThreadPoolExecutor(max_workers) as executor:
            for group in groups:
                avatar = self.helper().get_avatar(group)
                executor.submit(self.action.get_group, group, avatar=avatar, owner=owner)

    def get_max_workers(self, item):
        return len(item) if len(item) < 10 else 10

    def update_friends(self, bot):
        firends = bot.bot.friends(update=True)
        owner = bot.user
        max_workers = self.get_max_workers(firends)
        with ThreadPoolExecutor(max_workers) as executor:
            for firend in firends:
                avatar = self.helper().get_avatar(firend)
                executor.submit(self.action.get_user, firend, avatar=avatar, owner=owner, friend=True)


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
        self.save_message(msg)

    def save_message(self, msg):
        self.action.get_message(msg)

    def get_forward_url(self):
        timestamp = f'{int(time.time() * 1000)}'
        data = [self.app.app_id, self.app.token, timestamp]
        signature = create_signature(data)
        forward_url = f'{self.app.forward_url}?timestamp={timestamp}&signature={signature}'
        return forward_url
