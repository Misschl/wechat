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
    list_display = ['name', 'nick_name', 'remark_name', 'avatar_url', 'signature', 'sex', 'province', 'city',
                    'owner', 'puid', 'insert_time', 'update_time', ]

    readonly_fields = list_display

    def avatar_url(self, row):
        avatar = row.avatar
        if avatar:
            html = f'<img id="" src="{avatar}" width=38>'
            return mark_safe(html)
        return avatar

    avatar_url.short_description = '头像'


@admin.register(models.WxGroup)
class WxGroupAdmin(admin.ModelAdmin):
    pass
