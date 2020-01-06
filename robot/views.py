from django.shortcuts import HttpResponse

from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import RetrieveModelMixin, CreateModelMixin
from rest_framework.response import Response

from utils import views

from wxpy import Bot
from threading import Thread

from robot.core import robot

from . import serializers
from . import models
from . import authentication

import time


class LoginView(GenericViewSet):
    _qrcode = None
    _uuid = None
    _status = None
    serializer_class = serializers.AppModel
    queryset = models.AppModel.objects.all()

    def list(self, request, *args, **kwargs):
        """

        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        serializer = self.get_serializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        app: models.AppModel = serializer.validated_data
        # 这里要用多线程,不然登录的时候会一直阻塞住
        Thread(target=self.login, args=(app,)).start()
        response = self.get_response()
        return HttpResponse(response, content_type='image/png')

    def login(self, app: models.AppModel):
        cache_pkl = app.cache_pkl(delete=True)
        bot = Bot(qr_callback=self.qr_callback, cache_path=cache_pkl)
        bot = robot.Robot(bot, app)
        robot.quene.update({app.app_id: bot})
        result = self.check_bot_permissions(bot, app)
        return result

    @staticmethod
    def check_bot_permissions(bot, app):
        # if app.bind_user.puid != bot.bot.self.puid:
        #     raise Exception()
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


class GroupApi(views.ReadOnlyModelViewSet):
    """
    群组列表api
    list:
        群组列表
        :QueryParam: app_id  必填参数
        :QueryParam: app_secret  必填参数
    retrieve:
        单个群详情
        :QueryParam: app_id  必填参数
        :QueryParam: app_secret  必填参数
    """
    serializer_class = serializers.GroupModelSerializer
    authentication_classes = [authentication.AppAuthentication]
    queryset = models.WxGroup.objects.all()

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)


class FriendsApi(views.ReadOnlyModelViewSet):
    """
    好友列表api
    list:
        好友列表
        :QueryParam: app_id  必填参数
        :QueryParam: app_secret  必填参数

    retrieve:
        好友
        :QueryParam: app_id  必填参数
        :QueryParam: app_secret  必填参数
    """
    serializer_class = serializers.FriendsModelSerializer
    queryset = models.WxUser.objects.all()
    authentication_classes = [authentication.AppAuthentication]

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)


class MembersApi(RetrieveModelMixin, views.GenericViewSet):
    """
    retrieve:
        群成员
        :QueryParam: app_id  必填参数
        :QueryParam: app_secret  必填参数
    """
    serializer_class = serializers.GroupMembersModelSerializer
    authentication_classes = [authentication.AppAuthentication]
    queryset = models.WxGroup.objects.all()

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)


class SendMessageApi(CreateModelMixin, views.GenericViewSet):
    """
    create:
        主动发送消息接口
        msg_type---------为必填参数        选项为 ('text', 'image', 'file', 'video')
        puid             为必填参数        发送对象的唯一身份标识
        group            选填参数          bool值,当为true时,puid为群对象的puid
        text             选填/必填参数     当`msg_type`为`text`时,该参数必填, 为发送消息的文本内容
        url              选填/必填参数     当`msg_type`不为`text`时,该参数必填, 为发送消息的媒体的url
    """
    serializer_class = serializers.SendMessageSerializer
    authentication_classes = [authentication.AppAuthentication]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        try:
            bot = robot.quene.get(self.request.auth.app_id)
        except AttributeError:
            bot = None
        context.update({'bot': bot})
        return context


class MessageApi(RetrieveModelMixin, views.GenericViewSet):
    queryset = models.Message.objects.all()
    serializer_class = serializers.MessageModelSerializer
