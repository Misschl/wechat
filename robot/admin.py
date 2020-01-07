from django.contrib import admin
from django.utils.safestring import mark_safe

from . import models

# Register your models here.


admin.site.site_title = "WeChat后台管理"
admin.site.site_header = "WeChat"
admin.site.index_title = "GitHub"
admin.site.site_url = 'https://github.com/Ivy-1996/wechat'


@admin.register(models.AppModel)
class AppAdmin(admin.ModelAdmin):
    list_display = ['app_name', 'insert_time', 'update_time', 'app_id', 'app_secret', 'forward_url', 'debug_url',
                    'token', 'bind_user']

    readonly_fields = ['app_id', 'app_secret', 'bind_user']

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


@admin.register(models.WxMps)
class WxMpsAdmin(admin.ModelAdmin):
    list_display = ['name', 'nick_name', 'signature', 'province', 'city', 'owner']


@admin.register(models.Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['insert_time', 'type', 'send_user', 'send_group', 'receiver', 'maps']
    ordering = ['-insert_time']


@admin.register(models.TextMessage)
class TextMessageAdmin(admin.ModelAdmin):
    list_display = ['insert_time', 'text']


@admin.register(models.PictureMessage)
class PictureMessageAdmin(admin.ModelAdmin):
    list_display = ['src', 'file_name', 'img_height', 'img_width', 'insert_time', ]

    def src(self, row):
        url = row.url
        if url:
            html = f'<img id="" src="{url}" width=38>'
            return mark_safe(html)
        return url

    src.short_description = '图片预览'


@admin.register(models.RecordingMessage)
class RecordingMessageAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'src', 'voice_length', 'insert_time']

    def src(self, row):
        url = row.url
        if url:
            html = f'''<audio controls="controls">
            <source src="{url}" type="audio/ogg">
            </audio>'''
            return mark_safe(html)
        return url

    src.short_description = '点击播放'


@admin.register(models.VideoMessage)
class VideoMessageAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'src', 'play_length', 'insert_time']

    def src(self, row):
        html = f'<a href="{row.url}">点击播放</a>'
        return mark_safe(html)

    src.short_description = '点击播放'


@admin.register(models.AttachmentMessage)
class AttachmentMessageAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'src', 'file_size', 'insert_time']

    def src(self, row):
        html = f'<a href="{row.url}">点击下载</a>'
        return mark_safe(html)

    src.short_description = '点击下载'


@admin.register(models.MapMessage)
class MapMessageAdmin(admin.ModelAdmin):
    list_display = ['x', 'y', 'scale', 'link', 'maptype', 'poiname', 'poiid', 'text']

    def link(self, row):
        html = f'<a href="{row.url}">{row.label}</a>'
        return mark_safe(html)

    link.short_description = '位置详情'


@admin.register(models.SharingMessage)
class SharingMessageAdmin(admin.ModelAdmin):
    list_display = ['detail', 'title']

    def title(self, row):
        html = f'<a href="{row.url}">{row.text}</a>'
        return mark_safe(html)

    def detail(self, row):
        return '详情'

    detail.short_description = '详情'
