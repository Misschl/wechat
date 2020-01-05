from rest_framework import serializers

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
    class Meta:
        model = models.WxGroup
        fields = '__all__'


class FriendsModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WxUser
        fields = '__all__'


class GroupMembersModelSerializer(serializers.ModelSerializer):
    members = serializers.ManyRelatedField(child_relation=FriendsModelSerializer())

    class Meta:
        model = models.WxGroup
        fields = ['members']
