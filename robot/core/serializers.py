from django.db import transaction

from rest_framework import serializers

from robot import models
from robot import get_message_helper

from . import exception

from wxpy.api.bot import Group, Friend, MP, User
from wxpy.api.messages import Message
from wxpy.api.messages.sent_message import SentMessage

import pysnooper

helper = get_message_helper()


def action():
    from .action import SimpleAction
    return SimpleAction()


class AbstractSerializer:

    def save(self, **kwargs):
        context = self.get_obj(**kwargs)
        data = self.relate_serializer(instance=context).data
        data.update(kwargs)
        return self._save(data)

    def _save(self, data):
        raise NotImplemented()

    def get_obj(self, **kwargs):
        raise NotImplemented()

    @property
    def meta(self):
        return getattr(self, 'Meta')

    @property
    def relate_serializer(self):
        return getattr(self.meta, 'relate_serializer')

    @property
    def model(self):
        return getattr(self.meta, 'model')


class BotSerializer(serializers.Serializer):
    puid = serializers.CharField()
    name = serializers.CharField()
    nick_name = serializers.CharField()
    user_name = serializers.CharField()
    remark_name = serializers.CharField()
    signature = serializers.CharField()
    sex = serializers.IntegerField()
    province = serializers.CharField()
    city = serializers.CharField()


class GroupSerializer(serializers.Serializer):
    puid = serializers.CharField()
    name = serializers.CharField()
    nick_name = serializers.CharField()
    user_name = serializers.CharField()


class MpsSerializer(serializers.Serializer):
    puid = serializers.CharField()
    name = serializers.CharField()
    nick_name = serializers.CharField()
    province = serializers.CharField()
    city = serializers.CharField()
    signature = serializers.CharField()


class WxUserModelSerializer(AbstractSerializer, serializers.ModelSerializer):
    class Meta:
        model = models.WxUser
        relate_serializer = BotSerializer
        exclude = ['insert_time', 'update_time']
        extra_kwargs = {
            'owner': {'required': False},
            'avatar': {'required': False},
            'is_friend': {'required': False}
        }

    def get_obj(self, **kwargs):
        return self.context.get('user')

    def _save(self, data):
        user = self.get_obj()
        is_friend = True if user.is_friend is not None else False
        data.update({'is_friend': is_friend})
        return self.model.objects.update_or_create(defaults=data, puid=user.puid)[0]


class WxGroupModelSerializer(AbstractSerializer, serializers.ModelSerializer):
    class Meta:
        model = models.WxGroup
        exclude = ['insert_time', 'update_time']
        relate_serializer = GroupSerializer

    def get_obj(self, **kwargs):
        return self.context.get('group')

    def _save(self, data):
        group = self.get_obj()
        update_members = data.pop('update_members')
        instance = self.model.objects.update_or_create(defaults=data, puid=group.puid)[0]
        if update_members is True:
            self.get_members(group, data, instance)
        return instance

    def get_members(self, group, data, instance: models.WxGroup):
        members = group.members
        owner = data.get('owner')
        for member in members:
            avatar = helper().get_avatar(member)
            serializer = WxUserModelSerializer(context={'user': member})
            obj = serializer.save(avatar=avatar, owner=owner)
            instance.members.add(obj)


class WxMpsModelSerializer(AbstractSerializer, serializers.ModelSerializer):
    class Meta:
        model = models.WxMps
        relate_serializer = MpsSerializer
        exclude = ['insert_time', 'update_time']

    def get_obj(self, **kwargs):
        maps = self.context.get('maps')
        return maps

    def _save(self, data):
        maps = self.get_obj()
        bot_user = maps.bot.self
        puid = bot_user.puid
        owner = models.WxUser.objects.get(puid=puid)
        obj = self.model.objects.update_or_create(defaults=data, puid=maps.puid)[0]
        obj.owner = owner
        obj.save()
        return obj


class MessageMixin:

    @classmethod
    def save_receive_message(cls, message, instance, data):
        serializer = cls(instance=message)
        serializer_data = cls.get_serializer_data(serializer, message, instance, data)
        serializer = cls(data=serializer_data)
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    @classmethod
    def get_serializer_data(cls, serializer, message, instance, data):
        extra_data = cls.get_extra_data(serializer, message, instance, data)
        extra_data.update({'message': instance.id})
        extra_data.update(extra_data)
        return extra_data

    @classmethod
    def get_extra_data(cls, serializer, message, instance, data):
        return {}

    @classmethod
    @pysnooper.snoop()
    def save_send_message(cls, message, instance, data):
        print(message.path)
        path_list = message.path.split('\\')
        file_name = path_list[-1]
        url = '/media' + "".join(message.path.split('media')[1:]).replace('\\', '/')
        data = {'file_name': file_name, 'url': url}
        return cls.Meta.model.objects.create(**data)


class TextModelSerializer(MessageMixin, serializers.ModelSerializer):
    class Meta:
        model = models.TextMessage
        fields = '__all__'

    @classmethod
    def get_extra_data(cls, serializer, message, instance, data):
        return {'text': message.text}

    @classmethod
    def save_send_message(cls, message, instance, data):
        return cls.Meta.model.objects.create(**{'text': message.text})


class MapModelSerializer(MessageMixin, serializers.ModelSerializer):
    class Meta:
        model = models.MapMessage
        fields = '__all__'

    @classmethod
    def get_serializer_data(cls, serializer, message, instance, data):
        location = message.location
        location.update({'url': message.url, 'text': message.text, 'message': instance.id})
        return location


class SharingModelSerializer(MessageMixin, serializers.ModelSerializer):
    class Meta:
        model = models.SharingMessage
        fields = '__all__'

    @classmethod
    def get_extra_data(cls, serializer, message, instance, data):
        return {'text': message.text, 'url': message.url}


class PictureModelSerializer(MessageMixin, serializers.ModelSerializer):
    class Meta:
        model = models.PictureMessage
        fields = '__all__'

    @classmethod
    def get_serializer_data(cls, serializer, message, instance, data):
        url = helper(message=message).save_message_picture()
        serializer_data = serializer.data
        serializer_data.update({'message': instance.id, 'url': url})
        return serializer_data


class RecordingModelSerializer(MessageMixin, serializers.ModelSerializer):
    class Meta:
        model = models.RecordingMessage
        fields = '__all__'

    @classmethod
    def get_serializer_data(cls, serializer, message, instance, data):
        url = helper(message=message).save_message_recording()
        serializer_data = serializer.data
        serializer_data.update({'message': instance.id, 'url': url})
        return serializer_data


class AttachmentModelSerializer(MessageMixin, serializers.ModelSerializer):
    class Meta:
        model = models.AttachmentMessage
        fields = '__all__'

    @classmethod
    def get_serializer_data(cls, serializer, message, instance, data):
        url = helper(message=message).save_message_file()
        serializer_data = serializer.data
        serializer_data.update({'message': instance.id, 'url': url})
        return serializer_data


class VideoModelSerializer(MessageMixin, serializers.ModelSerializer):
    class Meta:
        model = models.VideoMessage
        fields = '__all__'

    @classmethod
    def get_serializer_data(cls, serializer, message, instance, data):
        url = helper(message=message).save_message_video()
        serializer_data = serializer.data
        serializer_data.update({'message': instance.id, 'url': url})
        return serializer_data


class MessageSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    type = serializers.CharField()
    create_time = serializers.DateTimeField()
    receive_time = serializers.DateTimeField()
    is_at = serializers.BooleanField(required=False, allow_null=True)


class MessageModelSerializer(AbstractSerializer, serializers.ModelSerializer):
    """
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
    """
    serializers_route = {
        'Text': TextModelSerializer,
        'Map': MapModelSerializer,
        'Sharing': SharingModelSerializer,
        'Picture': PictureModelSerializer,
        'Recording': RecordingModelSerializer,
        'Attachment': AttachmentModelSerializer,
        'Video': VideoModelSerializer,
    }

    class Meta:
        model = models.Message
        fields = '__all__'
        relate_serializer = MessageSerializer

    def get_obj(self, **kwargs):
        return self.context.get('message')

    @transaction.atomic
    @pysnooper.snoop()
    def _save(self, data: dict):
        # 设置保存点
        save_point = transaction.savepoint()
        # 获取消息对象
        message = self.get_obj()
        # 获取信息的属性
        """send_user, send_group, receiver, is_at, maps"""
        send_user, send_group, receiver, is_at, maps, receiver_group = self.get_extra_data(message)
        # 更新信息的基础属性
        data.update(
            {'send_user': send_user,
             'send_group': send_group,
             'receiver': receiver,
             'is_at': is_at,
             'maps': maps,
             'receiver_group': receiver_group
             }
        )
        owner = self.context.get('user')
        # 创建一条信息记录
        instance: models.Message = self.model.objects.create(**data, owner=owner)
        try:
            # 根据消息类型来获取不同的序列化器
            serializer_class = self.serializers_route.get(instance.type)
            # 保存信息
            if isinstance(message, Message):
                # 保存收到的信息
                handle = getattr(serializer_class, 'save_receive_message')
            elif isinstance(message, SentMessage):
                # 保存发出去的信息
                handle = getattr(serializer_class, 'save_send_message')
            else:
                raise exception.UnknowMsgTypeException()
            obj = handle(message, instance, data)
            return instance, obj
        except Exception as e:
            # 回滚
            transaction.savepoint_rollback(save_point)
            raise e

    def get_extra_data(self, obj: Message):
        sender = obj.sender
        receiver = obj.receiver

        # 获取发送方的信息
        if isinstance(sender, Group):
            send_group = action().get_group(sender, update_members=False)
            send_user = action().get_user(obj.member)
            is_at = obj.is_at
            maps = None
        elif isinstance(sender, Friend):
            send_user = action().get_user(sender)
            send_group = None
            is_at = None
            maps = None
        elif isinstance(sender, MP):
            send_user = None
            send_group = None
            is_at = None
            owner = self.context.get('user')
            maps = action().get_map(sender, owner=owner)
        else:
            raise exception.UnknowMsgTypeException()

        # 获取接受方的信息
        if isinstance(receiver, Friend):
            receiver = action().get_user(receiver)
            receiver_group = None
        elif isinstance(receiver, Group):
            receiver_group = action().get_group(receiver)
            receiver = None
        else:
            raise exception.UnknowMsgTypeException()

        return send_user, send_group, receiver, is_at, maps, receiver_group


class ReplyMessage(serializers.Serializer):
    msg_type = serializers.CharField()
    text = serializers.CharField(required=False, allow_blank=True)
    url = serializers.URLField(required=False)

    @property
    def reply_route(self):
        return {
            'text': action().reply_text,
            'image': action().reply_image,
            'file': action().reply_file,
            'video': action().reply_video,
        }

    def validate_msg_type(self, attrs):
        msg_type_list = ['text', 'image', 'video', 'file', 'recording']
        if attrs not in msg_type_list:
            raise serializers.ValidationError('非法的消息类型!')
        return attrs

    def validate(self, attrs):
        msg_type = attrs.get('msg_type')
        url = attrs.get('url')
        text = attrs.get('text')
        if msg_type != 'text' and url is None:
            raise serializers.ValidationError({'url': ['非文本类型url不可为空']})
        if msg_type == 'text' and text is None:
            raise serializers.ValidationError({'text': ['text类型text不可为空']})
        return attrs

    def save(self, **kwargs):
        message = self.context.get('message')
        msg_type = self.validated_data.get('msg_type')
        handle = self.reply_route.get(msg_type)
        reply_obj = handle(message, **self.validated_data)
        return reply_obj
