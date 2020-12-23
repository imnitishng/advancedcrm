# Generated by Django 3.1.1 on 2020-12-20 09:56

from django.db import migrations, models
import django.db.models.deletion
import marketingemails.customModelFields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SMSCampaign',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(max_length=20000)),
                ('creation_date', models.DateTimeField(verbose_name='date published')),
                ('audience', marketingemails.customModelFields.CommaSepField(blank=True)),
                ('remarket_audience', marketingemails.customModelFields.CommaSepField(blank=True)),
                ('parent_campaigns', marketingemails.customModelFields.CommaSepField(blank=True)),
                ('future_campaigns', marketingemails.customModelFields.CommaSepField(blank=True)),
                ('launch_datetime', models.DateTimeField(blank=True, verbose_name='date launched')),
                ('campaign_type', models.PositiveSmallIntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='ScheduledSMSCampaign',
            fields=[
                ('scheduled_timestamp', models.DateTimeField(db_index=True)),
                ('data', models.TextField()),
                ('campaign', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='campaign_to_schedule_queue', serialize=False, to='marketingtexts.smscampaign')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]