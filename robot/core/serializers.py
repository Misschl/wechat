from rest_framework import serializers

from robot import models


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


class WxUserModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WxUser
        exclude = ['insert_time', 'update_time']
        extra_kwargs = {
            'owner': {'required': False},
            'avatar': {'required': False},
            'is_friend': {'required': False}
        }

    def save(self, **kwargs):
        user = self.context.get('user')
        assert user is not None, 'WxUserModelSerializer实例化的时候需要在`content`里加上user=<Friend>'
        data = BotSerializer(instance=user).data
        data.update(kwargs)
        instance = self.Meta.model.objects.update_or_create(defaults=data, puid=user.puid)[0]
        return instance


class WxGroupModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WxGroup
        exclude = ['insert_time', 'update_time']

    def save(self, **kwargs):
        group = self.context.get('group')
        assert group is not None, 'WxGroupModelSerializer实例化的时候需要在`content`里加上group=<Group>'
        data = GroupSerializer(instance=group).data
        data.update(kwargs)
        instance = self.Meta.model.objects.update_or_create(defaults=data, puid=group.puid)[0]
        return instance
