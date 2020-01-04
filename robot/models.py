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
    app_id = models.CharField(max_length=50, null=True, blank=True)
    app_secret = models.CharField(max_length=50, null=True, blank=True)
    forward_url = models.URLField()
    debug_url = models.URLField()
    token = models.CharField(max_length=32)
    bind_user = models.OneToOneField('WxUser', on_delete=models.SET_NULL, null=True, blank=True)

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









class WxUser(BaseModel):
    SEX_CHOICES = (
        (1, '男'),
        (2, '女')
    )
    puid = models.CharField(max_length=15, primary_key=True)
    name = models.CharField(max_length=32, verbose_name='名称')
    nick_name = models.CharField(max_length=32, verbose_name='昵称')
    user_name = models.CharField(max_length=80, verbose_name='用户名')
    remark_name = models.CharField(max_length=32, verbose_name='备注名')
    avatar = models.URLField(verbose_name="头像")
    signature = models.CharField(max_length=255, verbose_name="签名")
    sex = models.IntegerField(choices=SEX_CHOICES, verbose_name="性别")
    province = models.CharField(max_length=15, verbose_name="省")
    city = models.CharField(max_length=15, verbose_name="市")
    is_friend = models.BooleanField(null=True)
    owner = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, related_name='wxuser_owner')

    class Meta:
        verbose_name_plural = verbose_name = '微信用户'

    def __str__(self):
        return self.remark_name or self.nick_name or self.name


class WxGroup(BaseModel):
    puid = models.CharField(max_length=15, primary_key=True)
    name = models.CharField(max_length=32)
    nick_name = models.CharField(max_length=32)
    user_name = models.CharField(max_length=80)
    avatar = models.URLField()
    members = models.ManyToManyField(WxUser, related_name='members')
    owner = models.OneToOneField(WxUser, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name_plural = verbose_name = '微信群组'
