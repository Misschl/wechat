# Generated by Django 2.1.5 on 2020-01-05 00:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('robot', '0007_auto_20200104_2350'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wxuser',
            name='remark_name',
            field=models.CharField(max_length=32, null=True, verbose_name='备注名'),
        ),
    ]