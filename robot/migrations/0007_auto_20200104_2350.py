# Generated by Django 2.1.5 on 2020-01-04 23:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('robot', '0006_auto_20200104_2147'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wxgroup',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='robot.WxUser'),
        ),
    ]
