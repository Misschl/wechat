# Generated by Django 2.1.5 on 2020-01-06 20:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('robot', '0021_message_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='receiver_group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='receiver_group', to='robot.WxGroup'),
        ),
    ]