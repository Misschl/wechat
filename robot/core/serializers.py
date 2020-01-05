from django.db import transaction

from rest_framework import serializers

from robot import models
from robot import get_message_helper

from . import exception

from wxpy.api.bot import Group, Friend
from wxpy.api.messages import Message

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


class TextModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TextMessage
        fields = '__all__'

    @classmethod
    def serializer_data(cls, data, instance, obj):
        data.update({'message': instance.id})
        return data


class MapModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MapMessage
        fields = '__all__'

    def get_new_instance(self, instance):
        return instance.location

    @classmethod
    def serializer_data(cls, data, instance, obj):
        data.update({'message': instance.id})
        return data


class SharingModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SharingMessage
        fields = '__all__'

    @classmethod
    def serializer_data(cls, data, instance, obj):
        data.update({'message': instance.id})
        return data


class PictureModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PictureMessage
        fields = '__all__'

    @classmethod
    def serializer_data(cls, data, instance, obj):
        url = helper(message=obj).save_message_picture()
        data.update({'message': instance.id, 'url': url})
        return data


class RecordingModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RecordingMessage
        fields = '__all__'

    @classmethod
    def serializer_data(cls, data, instance, obj):
        url = helper(message=obj).save_message_recording()
        data.update({'message': instance.id, 'url': url})
        return data


class AttachmentModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AttachmentMessage
        fields = '__all__'

    @classmethod
    def serializer_data(cls, data, instance, obj):
        url = helper(message=obj).save_message_file()
        data.update({'message': instance.id, 'url': url})
        return data


class VideoModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.VideoMessage
        fields = '__all__'

    @classmethod
    def serializer_data(cls, data, instance, obj):
        url = helper(message=obj).save_message_video()
        data.update({'message': instance.id, 'url': url})
        return data


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
    def _save(self, data: dict):
        save_point = transaction.savepoint()
        obj = self.get_obj()
        send_user, send_group, receiver, is_at = self.get_extra_data(obj)
        data.update({'send_user': send_user, 'send_group': send_group, 'receiver': receiver, 'is_at': is_at})
        instance: models.Message = self.model.objects.create(**data)
        try:
            serializer_class = self.serializers_route.get(instance.type)
            serializer = serializer_class(instance=obj)
            data = self.get_serializer_data(serializer.data, instance, obj, serializer_class)
            print(data)
            serializer = serializer_class(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            print(666)
            transaction.savepoint_rollback(save_point)
        except Exception as e:
            print(e)
            transaction.savepoint_rollback(save_point)

    def get_serializer_data(self, data: dict, instance: models.Message, obj, serializer_class):
        handle = getattr(serializer_class, 'serializer_data', self.get_default_serializer_data)
        return handle(data, instance, obj)

    def get_instance(self, instance, serializer_class):
        handle = getattr(serializer_class, 'get_new_instance', self.get_default_instance)
        return handle(instance)

    def get_default_instance(self, instance):
        return instance

    def get_default_serializer_data(self, data, instance, obj):
        return data

    def get_extra_data(self, obj: Message):
        sender = obj.sender
        receiver = obj.receiver
        if isinstance(sender, Group):
            send_group = action().get_group(sender, update_members=False)
            send_user = action().get_user(obj.member)
            is_at = obj.is_at
        elif isinstance(sender, Friend):
            send_user = action().get_user(sender)
            send_group = None
            is_at = None

        else:
            raise exception.UnknowMsgTypeException()
        print(type(sender))
        receiver = action().get_user(receiver)
        return send_user, send_group, receiver, is_at
