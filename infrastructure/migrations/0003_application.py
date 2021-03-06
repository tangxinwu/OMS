# Generated by Django 2.1.3 on 2018-11-29 02:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0002_auto_20181031_1629'),
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ApplicationName', models.CharField(max_length=100, verbose_name='应用名字')),
                ('ApplicationPath', models.CharField(max_length=200, verbose_name='应用在服务器上的路径')),
                ('ApplicationUpdateScriptPath', models.CharField(max_length=200, verbose_name='运行应用服务器上的部署脚本位置')),
                ('ApplicationServer', models.ForeignKey(on_delete='应用对应的服务器', to='infrastructure.Server')),
            ],
            options={
                'verbose_name_plural': '所有应用',
                'ordering': ['ApplicationName'],
            },
        ),
    ]
