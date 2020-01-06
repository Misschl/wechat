# Generated by Django 2.1.5 on 2020-01-06 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('robot', '0017_auto_20200105_2340'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attachmentmessage',
            name='file_name',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='picturemessage',
            name='file_name',
            field=models.CharField(blank=True, max_length=255, verbose_name='文件名'),
        ),
        migrations.AlterField(
            model_name='recordingmessage',
            name='file_name',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='videomessage',
            name='file_name',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
