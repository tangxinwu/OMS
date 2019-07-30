# Generated by Django 2.1.3 on 2018-11-30 02:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0006_application_filenameofzip'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='application',
            name='FileNameOfzip',
        ),
        migrations.AddField(
            model_name='application',
            name='Description',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='描述'),
        ),
        migrations.AlterField(
            model_name='application',
            name='ApplicationName',
            field=models.CharField(max_length=100, verbose_name='应用名字(只允许英文)'),
        ),
    ]
