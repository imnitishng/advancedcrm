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

    name = models.CharField(max_length=200)
    description = models.TextField(max_length=20000)
    creation_date = models.DateTimeField('date published')
    audience = CommaSepField(blank=True)
    parent_campaigns = CommaSepField(blank=True)

    def __str__(self):
        return self.name

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
