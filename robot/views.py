from django.shortcuts import HttpResponse

from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response

from wxpy import Bot
from threading import Thread

from robot.core import robot

from . import serializers
from . import models

import time


class LoginView(GenericViewSet):
    _qrcode = None
    _uuid = None
    _status = None
    serializer_class = serializers.AppModel

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        app: models.AppModel = serializer.validated_data
        # 这里要用多线程,不然登录的时候会一直阻塞住
        Thread(target=self.login, args=(app,)).start()
        response = self.get_response()
        return HttpResponse(response, content_type='image/png')
        # return response

    def login(self, app: models.AppModel):
        cache_pkl = app.cache_pkl(delete=True)
        bot = Bot(qr_callback=self.qr_callback, cache_path=cache_pkl)
        bot = robot.Robot(bot, app)
        robot.quene.update({app.app_id: bot})
        result = self.check_bot_permissions(bot, app)
        return result

    @staticmethod
    def check_bot_permissions(bot, app):
        if app.bind_user.puid != bot.bot.self.puid:
            raise Exception()
        return True

    # 递归查询二维码是否生成
    def get_response(self):
        # 这里要休眠0.1秒,避免两个线程获取同一个资源时不必要的资源消耗,也可以用锁锁住
        time.sleep(0.1)
        return self._qrcode if self._qrcode else self.get_response()

    # 获取二维码信息
    def qr_callback(self, uuid, status, qrcode):
        """
        :param uuid:
        :param status: 201【已扫描，未登录】200【已扫描，已登录】408【还未扫描】
        :param qrcode:
        :return:
        """
        self._qrcode = qrcode
        self._status = status
        self._uuid = uuid
