# Generated by Django 2.1.3 on 2018-12-14 08:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0010_applicationlogs'),
    ]

    operations = [
        migrations.AddField(
            model_name='applicationlogs',
            name='LogsFileName',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='日志文件名字（支持模糊搜索）'),
        ),
    ]
