# Generated by Django 2.1.5 on 2020-01-06 17:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('robot', '0020_auto_20200106_1717'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='msg_owner', to='robot.WxUser'),
        ),
    ]
