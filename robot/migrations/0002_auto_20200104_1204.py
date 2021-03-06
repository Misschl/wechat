# Generated by Django 2.1.5 on 2020-01-04 12:04

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('robot', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='appmodel',
            name='bind_user',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='robot.WxUser'),
        ),
        migrations.AddField(
            model_name='wxgroup',
            name='insert_time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='wxgroup',
            name='update_time',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='wxuser',
            name='insert_time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='wxuser',
            name='update_time',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
