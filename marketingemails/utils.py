import datetime
import math

from django.core.mail import get_connection, EmailMultiAlternatives
from django.utils.timezone import now as timezone_now

from .models import User, UserStatus, Campaigns, ScheduledCampaign

AUTOMATED_CAMPAIGN_MESSAGE = '''
\n\nThis is an automatically scheduled campaign, 
part of an a manually triggered parent campaign.
'''

def send_mass_html_mail(datatuple, fail_silently=False, user=None, password=None, 
                        connection=None):
    connection = connection or get_connection(username=user, password=password, 
    fail_silently=fail_silently)

    messages = []
    for subject, text, html, from_email, recipient in datatuple:
        message = EmailMultiAlternatives(subject, text, from_email, [recipient])
        message.attach_alternative(html, 'text/html')
        messages.append(message)
    return connection.send_messages(messages)

def dictionary_to_str(dic):
    pass

def schedule_future_campaign(reps, user_ids, parent_campaign):    
    '''
    Schedule all future campaign entries based on the number selected 
    in the view. The campaigns are dummy right now, audience is added later.
    '''
    campaign_parents = []
    rount_diff = int(reps)//3
    campaign_round = 0

    previous_campaign_id = parent_campaign.id
    for i in range(int(reps)):
        campaign_name = parent_campaign.name + '-' + str(i+1)
        campaign_desc = parent_campaign.description + AUTOMATED_CAMPAIGN_MESSAGE
        campaign_parents.append(previous_campaign_id)
        campaign_launch_time = timezone_now() + datetime.timedelta(days=i+1)

        scheduled_campaign = Campaigns(
            name = campaign_name,
            description = campaign_desc,
            creation_date = timezone_now(),
            launch_datetime = campaign_launch_time,
            parent_campaigns = campaign_parents
        )
        scheduled_campaign.save()
        previous_campaign_id = scheduled_campaign.id
        
        campaign_round += rount_diff
        if campaign_round > 3:
            campaign_round = 3
        campaign_queue_entry = ScheduledCampaign(
            type = campaign_round,
            scheduled_timestamp = campaign_launch_time,
            campaign = scheduled_campaign
        )
        campaign_queue_entry.save()
        