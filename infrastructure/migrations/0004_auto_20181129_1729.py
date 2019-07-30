# Generated by Django 2.1.3 on 2018-11-29 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0003_application'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='ApplicationUpdateScriptPathAfter',
            field=models.CharField(blank=True, null=True, max_length=200, verbose_name='复制到远程服务器运行脚本的位置'),
        ),
        migrations.AlterField(
            model_name='application',
            name='ApplicationUpdateScriptPath',
            field=models.CharField(max_length=200, verbose_name='运行devops服务器上的脚本位置'),
        ),
    ]