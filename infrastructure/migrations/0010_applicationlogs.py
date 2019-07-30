# Generated by Django 2.1.3 on 2018-12-12 03:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0009_auto_20181211_1808'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApplicationLogs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('LogsOfApplication', models.CharField(max_length=50, verbose_name='什么应用的日志')),
                ('PathOfLogs', models.CharField(max_length=150, verbose_name='日志的路径')),
                ('Description', models.CharField(blank=True, max_length=300, null=True, verbose_name='描述')),
                ('ApplicationOnTheServer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='infrastructure.Server')),
            ],
            options={
                'verbose_name_plural': '所有应用的日志',
                'ordering': ['ApplicationOnTheServer'],
            },
        ),
    ]