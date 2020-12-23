import datetime

from django.utils.timezone import now as timezone_now
from django.shortcuts import get_list_or_404, get_object_or_404, render, redirect

from marketingemails.models import User, UserStatus, Campaigns, ScheduledCampaign
from marketingtexts.models import SMSCampaign, ScheduledSMSCampaign
from reports.utils import users_interactions_single_campaign

from marketingemails.lib.send_mail import send_campaign_mails
from marketingemails.lib.send_sms import send_campaign_sms


AUTOMATED_CAMPAIGN_MESSAGE = '''
\n\nThis is an automatically scheduled campaign, 
part of an a manually triggered parent campaign.
'''

def schedule_future_campaign(reps, user_ids, parent_campaign, campaign_mode):
    '''
    Schedule all future campaign entries based on the number selected 
    in the view. The campaigns are dummy right now, audience is added later.
    '''
    campaign_parents = []
    child_campaigns = []
    round_diff = int(reps)//3
    campaign_round = 1

    previous_campaign_id = parent_campaign.id
    for i in range(int(reps)):
        campaign_name = parent_campaign.name + '-' + str(i+1)
        campaign_desc = parent_campaign.description + AUTOMATED_CAMPAIGN_MESSAGE
        campaign_parents.append(previous_campaign_id)
        campaign_launch_time = timezone_now() + datetime.timedelta(days=i+1)

        if (round_diff != 0 and i % round_diff) == 0:
            campaign_round += 1
        if campaign_round > 3:
            campaign_round = 3

        if campaign_mode == 'sms':
            scheduled_campaign = SMSCampaign(
                name = campaign_name,
                description = campaign_desc,
                creation_date = timezone_now(),
                launch_datetime = campaign_launch_time,
                parent_campaigns = campaign_parents,
                campaign_type = campaign_round
            )
            scheduled_campaign.save()
            previous_campaign_id = scheduled_campaign.id
            child_campaigns.append(scheduled_campaign.id)
            
            campaign_queue_entry = ScheduledSMSCampaign(
                scheduled_timestamp = campaign_launch_time,
                campaign = scheduled_campaign
            )
            campaign_queue_entry.save()
        elif campaign_mode == 'emails':
            scheduled_campaign = Campaigns(
                name = campaign_name,
                description = campaign_desc,
                creation_date = timezone_now(),
                launch_datetime = campaign_launch_time,
                parent_campaigns = campaign_parents,
                campaign_type = campaign_round
            )
            scheduled_campaign.save()
            previous_campaign_id = scheduled_campaign.id
            child_campaigns.append(scheduled_campaign.id)
            
            campaign_queue_entry = ScheduledCampaign(
                scheduled_timestamp = campaign_launch_time,
                campaign = scheduled_campaign
            )
            campaign_queue_entry.save()

    parent_campaign.future_campaigns = child_campaigns
    parent_campaign.save()


def deliver_campaign(job, job_type):
    '''
    Parent function used to deliver every scheduled campaigns be it child or parent
    '''
    
    if job.campaign.parent_campaigns[0]:
        # Child campaign
        previous_campaign_id = job.campaign.parent_campaigns[-1]
        
        if job_type == 'email':
            previous_campaign = get_object_or_404(Campaigns, pk=previous_campaign_id)
        elif job_type == 'sms':
            previous_campaign = get_object_or_404(SMSCampaign, pk=previous_campaign_id)

        previous_campaign_user_ids = previous_campaign.audience
        if previous_campaign_user_ids[0] == '':
            previous_campaign_user_ids = []
        if len(previous_campaign.remarket_audience) > 1:
            previous_campaign_user_ids.extend(previous_campaign.remarket_audience)

        previous_campaign_users = User.objects.in_bulk(previous_campaign_user_ids)

        if previous_campaign_users:
            previous_campaign_users = list(previous_campaign_users.values())
        users_interaction, previous_campaign_interactions = users_interactions_single_campaign(previous_campaign_users, previous_campaign_id)

        campaign_to_send = job.campaign
        next_marketing_campaign, remarketing_campaign = configure_campaigns(users_interaction, campaign_to_send, job_type)    
        
        if job_type == 'email':
            send_campaign_mails(next_marketing_campaign)
            send_campaign_mails(remarketing_campaign)
        elif job_type == 'sms':
            send_campaign_sms(next_marketing_campaign)
            send_campaign_sms(remarketing_campaign)
        job.delete()
    else:
        # Parent Campaign
        if job_type == 'sms':
            campaign_to_send = job.campaign
            status = send_campaign_sms(campaign_to_send)
            if status:
                job.delete()
    
    
def configure_campaigns(previous_users_interactions, campaign, campaign_type):
    '''
    Configure the next automatic marketing or remarketing campaign 
    based on the response of the previous campaign.
    '''
    users_qualified = []
    users_not_qualified = []
    
    for interaction in previous_users_interactions:
        if (campaign_type == 'email' and interaction.get('total_interactions') > 1) or 
        (campaign_type == 'sms' and interaction.get('total_interactions') >= 1):
            users_qualified.append(interaction['id'])
        else:
            users_not_qualified.append(interaction['id'])

    campaign.audience = users_qualified
    campaign.remarket_audience = users_not_qualified
    campaign.save()

    remarketing_campaign = configure_remarketing_campaign(users_not_qualified, campaign_type)

    return campaign, remarketing_campaign


def configure_remarketing_campaign(users, campaign_type):

    if campaign_type == 'email':
        remarketing_campaign = get_object_or_404(Campaigns, name='Remarketing Campaign')
    elif campaign_type == 'sms':
        remarketing_campaign = get_object_or_404(SMSCampaign, name='Remarketing Campaign')

    remarketing_campaign.audience = users
    remarketing_campaign.save()

    return remarketing_campaign
