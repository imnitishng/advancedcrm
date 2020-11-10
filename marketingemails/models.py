import datetime

from django.db import models
from .customModelFields import CommaSepField, HashmapField


class User(models.Model):
    
    name = models.CharField(max_length=200)
    email_address = models.CharField(max_length=200)  
    phone_number = models.CharField(max_length=20, blank=True)
    location_of_interest = models.CharField(max_length=100, default='NULL')  
    city = models.CharField(max_length=100, default='NULL')  
    marketing_link = models.CharField(max_length=500, default='NULL')
    join_date = models.DateTimeField('date published')

    participated_campaigns = CommaSepField(blank=True)

    def __str__(self):
        return self.name


class Campaigns(models.Model):
    '''
    Future Campaigns = Campaign IDs of the campaigns scheduled for future
    Parent Campaigns = Campaign IDs of the campaigns parent campaigns that have been sent

    Campaign Types:
        ROUND1 = 1
        ROUND2 = 2
        ROUND3 = 3
        REMARKETING = 99
    '''

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


class UserStatus(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='user_to_status'
    )
    email_opens = HashmapField(blank=True)
    link_opens = HashmapField(blank=True)

    def __str__(self):
        return self.user.name


class AbstractScheduledJob(models.Model):
    scheduled_timestamp: datetime.datetime = models.DateTimeField(db_index=True)
    data: str = models.TextField()

    class Meta:
        abstract = True


class ScheduledCampaign(AbstractScheduledJob):
    campaign = models.OneToOneField(
        Campaigns,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='campaign_to_schedule_queue'
    )
    
    def __str__(self) -> str:
        return f"Campaign `{self.campaign.name}` scheduled for: {self.scheduled_timestamp.strftime('%d %b %Y - %I:%M%p')}"
