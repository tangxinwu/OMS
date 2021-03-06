# Generated by Django 2.1.2 on 2018-10-31 06:28

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Server',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('server_name', models.CharField(max_length=50, verbose_name='服务器名字')),
                ('wan_ip', models.GenericIPAddressField(verbose_name='外网ip')),
                ('lan_ip', models.GenericIPAddressField(verbose_name='内网ip')),
                ('applications', models.CharField(blank=True, max_length=500, null=True, verbose_name='应用')),
                ('descriptions', models.CharField(blank=True, max_length=500, null=True, verbose_name='描述')),
            ],
        ),
    ]
