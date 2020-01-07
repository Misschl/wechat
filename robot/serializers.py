from rest_framework import serializers
from robot.core.action import SimpleAction
from robot.core.serializers import TextModelSerializer, PictureModelSerializer, AttachmentModelSerializer, \
    VideoModelSerializer
from robot import core

from . import models


class AppModel(serializers.ModelSerializer):
    class Meta:
        model = models.AppModel
        fields = ['app_id', 'app_secret']
        extra_kwargs = {
            'app_id': {'required': True},
            'app_secret': {'required': True},
        }

    def validate(self, attrs):
        app_id = attrs.get('app_id')
        app_secret = attrs.get('app_secret')
        try:
            app = self.Meta.model.objects.get(app_id=app_id, app_secret=app_secret)
        except self.Meta.model.DoesNotExist:
            raise serializers.ValidationError({'errmsg': ['无效的app_id或app_secret']})
        return app


# class AppAuthenticationSerializer(serializers.ModelSerializer):
#     app_id = serializers.CharField()
#     app_secret = serializers.CharField()


class GroupModelSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = models.WxGroup
        exclude = ['members']

    def get_member_count(self, row):
        return row.members.count()


class FriendsModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WxUser
        fields = '__all__'


class GroupMembersModelSerializer(serializers.ModelSerializer):
    members = serializers.ManyRelatedField(child_relation=FriendsModelSerializer())

    class Meta:
        model = models.WxGroup
        fields = ['members']


class SendMessageSerializer(serializers.Serializer):
    """asdasda"""
    msg_type = serializers.CharField(help_text='消息类型')
    puid = serializers.CharField()
    group = serializers.BooleanField(required=False)
    text = serializers.CharField(required=False)
    url = serializers.URLField(required=False)

    serializers_route = {
        'text': TextModelSerializer,
        'picture': PictureModelSerializer,
        'file': AttachmentModelSerializer,
        'video': VideoModelSerializer,
    }

    def validate_msg_type(self, attrs):
        msg_type_list = ['text', 'image', 'video', 'file']
        if attrs not in msg_type_list:
            raise serializers.ValidationError({'msg_type_list': ['非法的消息类型']})
        return attrs

    def validate(self, attrs):
        msg_type = attrs.get('msg_type')
        text = attrs.get('text')
        url = attrs.get('url')
        if msg_type == 'text' and text is None:
            raise serializers.ValidationError({'text': ['msg_type为text时,text为必填参数']})
        if msg_type != 'text' and url is None:
            raise serializers.ValidationError({'text': [f'msg_type为{msg_type}时,url为必填参数']})
        return attrs

    def save(self, **kwargs):
        bot = self.context.get('bot')
        action = SimpleAction(bot=bot.bot)
        handle = getattr(action, f'send_{self.validated_data.get("msg_type")}')
        reply_obj = handle(**self.validated_data)
        return reply_obj


class MessageModelSerializer(serializers.ModelSerializer):
    content = serializers.SerializerMethodField()

    class Meta:
        model = models.Message
        fields = '__all__'
        extra_kwargs = {
            'create_time': {'format': '%Y-%m-%d %H:%M:%S'},
            'receive_time': {'format': '%Y-%m-%d %H:%M:%S'},
        }

    def get_content(self, row):
        msg_type = row.type
        instance = getattr(row, f'{msg_type.lower()}message')
        serializer_class = getattr(core.serializers, f'{msg_type.title()}ModelSerializer')
        serializer = serializer_class(instance=instance)
        return serializer.data
