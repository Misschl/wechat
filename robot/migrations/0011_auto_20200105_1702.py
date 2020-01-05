# Generated by Django 2.1.5 on 2020-01-05 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('robot', '0010_auto_20200105_1342'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='appmodel',
            options={'verbose_name': '对接应用', 'verbose_name_plural': '对接应用'},
        ),
        migrations.AlterField(
            model_name='message',
            name='is_at',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AlterField(
            model_name='wxuser',
            name='friend',
            field=models.BooleanField(null=True, verbose_name='我的好友'),
        ),
        migrations.AlterField(
            model_name='wxuser',
            name='is_friend',
            field=models.BooleanField(null=True, verbose_name='和我有好友关系'),
        ),
        migrations.AlterField(
            model_name='wxuser',
            name='puid',
            field=models.CharField(help_text='微信用户的外键', max_length=15, primary_key=True, serialize=False),
        ),
    ]
