# Generated by Django 3.1.1 on 2020-11-10 08:38

from django.db import migrations
import marketingemails.customModelFields


class Migration(migrations.Migration):

    dependencies = [
        ('marketingemails', '0007_auto_20201110_0756'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaigns',
            name='remarket_audience',
            field=marketingemails.customModelFields.CommaSepField(blank=True),
        ),
    ]
