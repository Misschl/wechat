from django.contrib import admin
from django.utils.safestring import mark_safe

from . import models


# Register your models here.

@admin.register(models.AppModel)
class AppAdmin(admin.ModelAdmin):
    list_display = ['insert_time', 'update_time', 'app_id', 'app_secret', 'forward_url', 'debug_url', 'token',
                    'bind_user']

    readonly_fields = ['app_id', 'app_secret']

    def save_model(self, request, obj, form, change):
        result = super().save_model(request, obj, form, change)
        if change is False:
            app_id, app_secret = models.AppModel.create_app()
            obj.app_id = app_id
            obj.app_secret = app_secret
            obj.save()
        return result


@admin.register(models.WxUser)
class WxUserAdmin(admin.ModelAdmin):
    search_fields = ['name', 'nick_name', 'remark_name', 'signature', 'sex', 'province', 'city', 'puid', 'insert_time',
                     'update_time', 'friend', 'is_friend']
    list_display = ['avatar_url'] + search_fields

    readonly_fields = list_display

    list_filter = ['is_friend', 'owner', 'sex', 'province', 'city', 'friend']

    ordering = ['name', 'nick_name', 'remark_name']

    def avatar_url(self, row):
        avatar = row.avatar
        if avatar:
            html = f'<img id="" src="{avatar}" width=38>'
            return mark_safe(html)
        return avatar

    avatar_url.short_description = '头像'


@admin.register(models.WxGroup)
class WxGroupAdmin(admin.ModelAdmin):
    list_display = ['avatar_url', 'name', 'nick_name', 'owner', 'member_count']
    readonly_fields = list_display + ['members', 'user_name', 'puid', 'avatar']
    list_display_links = ['avatar_url', 'name']

    def avatar_url(self, row):
        avatar = row.avatar
        if avatar:
            html = f'<img id="" src="{avatar}" width=38>'
            return mark_safe(html)
        return avatar

    def member_count(self, row):
        return row.members.count()

    avatar_url.short_description = '头像'
    member_count.short_description = '群员数'


@admin.register(models.Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['insert_time', 'type', 'send_user', 'send_group', 'receiver', 'maps']
