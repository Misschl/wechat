# Generated by Django 2.1.5 on 2020-01-04 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('robot', '0003_auto_20200104_1236'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appmodel',
            name='insert_time',
            field=models.DateTimeField(auto_now_add=True, verbose_name='插入时间'),
        ),
        migrations.AlterField(
            model_name='appmodel',
            name='update_time',
            field=models.DateTimeField(auto_now=True, verbose_name='更新时间'),
        ),
        migrations.AlterField(
            model_name='wxgroup',
            name='insert_time',
            field=models.DateTimeField(auto_now_add=True, verbose_name='插入时间'),
        ),
        migrations.AlterField(
            model_name='wxgroup',
            name='update_time',
            field=models.DateTimeField(auto_now=True, verbose_name='更新时间'),
        ),
        migrations.AlterField(
            model_name='wxuser',
            name='insert_time',
            field=models.DateTimeField(auto_now_add=True, verbose_name='插入时间'),
        ),
        migrations.AlterField(
            model_name='wxuser',
            name='is_friend',
            field=models.BooleanField(null=True),
        ),
        migrations.AlterField(
            model_name='wxuser',
            name='update_time',
            field=models.DateTimeField(auto_now=True, verbose_name='更新时间'),
        ),
    ]
