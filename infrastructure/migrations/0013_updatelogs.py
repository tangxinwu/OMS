# Generated by Django 2.1.3 on 2019-01-15 09:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0012_remoteserverservice'),
    ]

    operations = [
        migrations.CreateModel(
            name='UpdateLogs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('UpdateName', models.CharField(max_length=200, verbose_name='更新的中文名字')),
                ('UpdateTaskId', models.CharField(max_length=200, verbose_name='更新的taskID')),
            ],
            options={
                'verbose_name_plural': '更新日志',
                'ordering': ['UpdateName'],
            },
        ),
    ]