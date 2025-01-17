# Generated by Django 3.1.1 on 2020-10-22 09:26

from django.db import migrations, models
import django.db.models.deletion
import marketingemails.customModelFields


class Migration(migrations.Migration):

    dependencies = [
        ('marketingemails', '0002_auto_20201021_0912'),
    ]

    operations = [
        migrations.CreateModel(
            name='Campaigns',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(max_length=20000)),
                ('creation_date', models.DateTimeField(verbose_name='date published')),
                ('audience', marketingemails.customModelFields.CommaSepField(default='NULL')),
                ('parent_campaigns', marketingemails.customModelFields.CommaSepField(default='NULL')),
            ],
        ),
        migrations.CreateModel(
            name='UserStatus',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='user_to_status', serialize=False, to='marketingemails.user')),
                ('email_opens', marketingemails.customModelFields.HashmapField(default='NULL')),
                ('link_opens', marketingemails.customModelFields.HashmapField(default='NULL')),
            ],
        ),
    ]
