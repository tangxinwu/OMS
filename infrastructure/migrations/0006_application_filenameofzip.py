# Generated by Django 2.1.3 on 2018-11-30 02:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0005_auto_20181129_1750'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='FileNameOfzip',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='打好包的文件名字'),
        ),
    ]
