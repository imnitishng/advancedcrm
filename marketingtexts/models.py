from django.db import models

from marketingemails.customModelFields import CommaSepField, HashmapField
from marketingemails.models import AbstractScheduledJob


class SMSCampaign(models.Model):    
    name = models.CharField(max_length=200)
    description = models.TextField(max_length=20000)
    creation_date = models.DateTimeField('date published')
    audience = CommaSepField(blank=True)
    remarket_audience = CommaSepField(blank=True)
    parent_campaigns = CommaSepField(blank=True)
    future_campaigns = CommaSepField(blank=True)
    launch_datetime = models.DateTimeField('date launched', blank=True)
    campaign_type = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return f"{self.name}  |  Trigger Time: {self.launch_datetime.strftime('%d, %b %Y - %I:%M%p')}"


class ScheduledSMSCampaign(AbstractScheduledJob):
    campaign = models.OneToOneField(
        SMSCampaign,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='campaign_to_schedule_queue'
    )

    def __str__(self) -> str:
        return f"Campaign `{self.campaign.name}` scheduled for: {self.scheduled_timestamp.strftime('%d %b %Y - %I:%M%p')}"