# Generated by Django 2.1.2 on 2018-10-31 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('login_name', models.CharField(max_length=50, verbose_name='登陆的名字')),
                ('xshell_path', models.CharField(blank=True, max_length=200, null=True, verbose_name='xshell路径')),
                ('login_password', models.CharField(max_length=100, verbose_name='登陆的密码')),
            ],
            options={
                'verbose_name_plural': '所有注册能登陆的用户',
                'ordering': ['login_name'],
            },
        ),
        migrations.AlterModelOptions(
            name='server',
            options={'ordering': ['server_name'], 'verbose_name_plural': '所有服务器'},
        ),
        migrations.AddField(
            model_name='server',
            name='password',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='登陆密码'),
        ),
    ]
