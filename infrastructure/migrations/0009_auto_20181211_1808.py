# Generated by Django 2.1.3 on 2018-12-11 10:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0008_auto_20181211_1415'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='ApplicationServer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='infrastructure.Server'),
        ),
    ]