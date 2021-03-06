from django.db import models
from django.conf import settings
import os

import uuid


# Create your models here.

class BaseModel(models.Model):
    insert_time = models.DateTimeField(auto_now_add=True, verbose_name='插入时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        abstract = True


class AppModel(BaseModel):
    app_name = models.CharField(max_length=20, help_text='app的名称', verbose_name='名称')
    app_id = models.CharField(max_length=50, null=True, blank=True)
    app_secret = models.CharField(max_length=50, null=True, blank=True)
    forward_url = models.URLField(verbose_name='转发的网址', help_text='收到的微信消息都会发送到该url上')
    debug_url = models.URLField(verbose_name='debug网址', help_text='错误和调试信息会发送到该网址上')
    token = models.CharField(max_length=32, help_text='生成签名的必要参数', verbose_name='token')
    bind_user = models.OneToOneField('WxUser', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="绑定的微信用户")

    class Meta:
        verbose_name_plural = verbose_name = '对接应用'

    @classmethod
    def create_app(cls):
        app_id, app_secret = uuid.uuid4().hex, uuid.uuid1().hex
        try:
            cls.objects.get(app_id=app_id)
        except cls.DoesNotExist:
            return app_id, app_secret
        return cls.create_app()

    @property
    def puid_pkl(self):
        """存储puid  pkl的路径  保证信息的唯一性"""
        return os.path.join(settings.PKL_PATH, f'{self.app_id}_puid.pkl')

    def cache_pkl(self, delete=False):
        cache_pkl = os.path.join(settings.PKL_PATH, f'{self.app_id}_cache.pkl')
        """重新登录的时候需要删除原来的,不然会卡在那里"""
        if delete is True:
            try:
                os.remove(cache_pkl)
            except FileNotFoundError:
                pass
        return cache_pkl

    def __str__(self):
        return self.app_name


class WxUser(BaseModel):
    SEX_CHOICES = (
        (1, '男'),
        (2, '女')
    )
    puid = models.CharField(max_length=15, primary_key=True, help_text='微信用户的外键', verbose_name='PUID')
    name = models.CharField(max_length=32, verbose_name='名称', null=True)
    nick_name = models.CharField(max_length=32, verbose_name='昵称', null=True)
    user_name = models.CharField(max_length=80, verbose_name='用户名', null=True)
    remark_name = models.CharField(max_length=32, verbose_name='备注名', null=True)
    avatar = models.URLField(verbose_name="头像")
    signature = models.CharField(max_length=255, verbose_name="签名", null=True)
    sex = models.IntegerField(choices=SEX_CHOICES, verbose_name="性别", null=True)
    province = models.CharField(max_length=15, verbose_name="省", null=True)
    city = models.CharField(max_length=15, verbose_name="市", null=True)
    is_friend = models.BooleanField(null=True, verbose_name='和我有好友关系')
    friend = models.BooleanField(null=True, verbose_name='我的好友')
    owner = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, related_name='wxuser_owner')

    class Meta:
        verbose_name_plural = verbose_name = '微信用户'

    def __str__(self):
        return self.remark_name or self.nick_name or self.name


class WxGroup(BaseModel):
    puid = models.CharField(max_length=15, primary_key=True)
    name = models.CharField(max_length=32, verbose_name='名称')
    nick_name = models.CharField(max_length=32, verbose_name='昵称')
    user_name = models.CharField(max_length=80)
    avatar = models.URLField(verbose_name='头像')
    members = models.ManyToManyField(WxUser, related_name='members', verbose_name='群员')
    owner = models.ForeignKey(WxUser, on_delete=models.SET_NULL, null=True, verbose_name='群归属')

    class Meta:
        verbose_name_plural = verbose_name = '微信群组'


class WxMps(BaseModel):
    puid = models.CharField(max_length=15, primary_key=True)
    name = models.CharField(max_length=32, verbose_name='名称')
    nick_name = models.CharField(max_length=32, verbose_name='昵称')
    province = models.CharField(max_length=15, verbose_name="省", null=True)
    city = models.CharField(max_length=15, verbose_name="市", null=True)
    signature = models.CharField(max_length=255, verbose_name="签名", null=True)
    owner = models.ForeignKey(WxUser, on_delete=models.SET_NULL, null=True, verbose_name='群归属')

    class Meta:
        verbose_name_plural = verbose_name = '微信公众号'

    def __str__(self):
        return self.name


class Message(BaseModel):
    TYPE_CHOICES = (
        ('Text', '文本'),
        ('Map', '位置'),
        ('Card', '名片'),
        ('Note', '提示'),
        ('Sharing', '分享'),
        ('Picture', '图片'),
        ('Recording', '语音'),
        ('Attachment', '文件'),
        ('Video', '视频'),
        ('Friends', '好友请求'),
        ('System', '系统'),
    )
    id = models.BigIntegerField(primary_key=True)
    type = models.CharField(max_length=15, choices=TYPE_CHOICES, verbose_name='消息类型')
    create_time = models.DateTimeField(verbose_name='创建时间')
    receive_time = models.DateTimeField(verbose_name='接受时间')
    is_at = models.BooleanField(default=False, null=True, verbose_name='是否@')
    send_user = models.ForeignKey(WxUser, on_delete=models.SET_NULL, null=True, related_name='send_user',
                                  verbose_name='主动发送消息的用户')
    send_group = models.ForeignKey(WxGroup, on_delete=models.SET_NULL, null=True, verbose_name='主动发送消息的群组')
    maps = models.ForeignKey(WxMps, on_delete=models.SET_NULL, null=True, verbose_name='公众号')
    receiver = models.ForeignKey(WxUser, on_delete=models.SET_NULL, null=True, related_name='receiver',
                                 verbose_name='接受信息的用户')
    receiver_group = models.ForeignKey(WxGroup, on_delete=models.SET_NULL, null=True, related_name='receiver_group',
                                       verbose_name='接受信息的群组')
    owner = models.ForeignKey(WxUser, on_delete=models.SET_NULL, null=True, related_name='msg_owner',
                              verbose_name='信息的拥有者')

    class Meta:
        verbose_name = verbose_name_plural = '消息记录'

    def __str__(self):
        return f'{self.type}-{self.owner.name}'


class BaseMessage(BaseModel):
    message = models.OneToOneField(Message, on_delete=models.SET_NULL, null=True)

    class Meta:
        abstract = True


class TextMessage(BaseMessage):
    text = models.CharField(max_length=2048, verbose_name='文本内容')

    class Meta:
        verbose_name = verbose_name_plural = '文本消息'


class MapMessage(BaseMessage):
    x = models.FloatField()
    y = models.FloatField()
    scale = models.IntegerField()
    label = models.CharField(max_length=255)
    maptype = models.IntegerField()
    poiname = models.CharField(max_length=255)
    poiid = models.CharField(max_length=255, blank=True)
    url = models.CharField(max_length=500)
    text = models.CharField(max_length=255)

    class Meta:
        verbose_name = verbose_name_plural = '位置消息'


class SharingMessage(BaseMessage):
    url = models.CharField(max_length=500)
    text = models.CharField(max_length=50)

    class Meta:
        verbose_name = verbose_name_plural = '分享消息'


class PictureMessage(BaseMessage):
    file_name = models.CharField(max_length=255, verbose_name='文件名', blank=True)
    url = models.CharField(verbose_name='文件地址', max_length=500)
    img_height = models.IntegerField(verbose_name='图片高度', null=True)
    img_width = models.IntegerField(verbose_name='图片宽度', null=True)

    class Meta:
        verbose_name = verbose_name_plural = '图片消息'


class RecordingMessage(BaseMessage):
    voice_length = models.BigIntegerField(null=True, verbose_name='录音时间')
    url = models.CharField(max_length=500)
    file_name = models.CharField(max_length=255, blank=True, verbose_name='文件名')

    class Meta:
        verbose_name = verbose_name_plural = '录音消息'


class AttachmentMessage(BaseMessage):
    file_name = models.CharField(max_length=255, blank=True)
    file_size = models.CharField(max_length=20, null=True)
    url = models.CharField(max_length=500)

    class Meta:
        verbose_name = verbose_name_plural = '文件消息'


class VideoMessage(BaseMessage):
    play_length = models.IntegerField(null=True)
    file_name = models.CharField(max_length=255, blank=True)
    url = models.CharField(max_length=500)

    class Meta:
        verbose_name = verbose_name_plural = '视频消息'


class Friends(BaseMessage):
    text = models.CharField(max_length=255)

    class Meta:
        verbose_name = verbose_name_plural = '好友请求'
