from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse
from django.shortcuts import get_list_or_404, get_object_or_404, render, redirect
from django.core.mail import get_connection, EmailMultiAlternatives
from django.template.loader import render_to_string

from marketingemails.models import User, UserStatus, Campaigns

def users_interactions_single_campaign(all_users, campaign_id):
    '''
    Takes as input the `User` object and campaign and returns
    the interactions as a dictionary and total campaign 
    impressions.
    '''
    users_for_campaign = []
    campaign_interactions = 0
    for user in all_users:
        if campaign_id in user.participated_campaigns:
            user_status = get_object_or_404(UserStatus, pk=user.id)
            email_interactions = user_status.email_opens.get(campaign_id, 0)
            link_interactions = user_status.link_opens.get(campaign_id, 0)
            total_interactions = email_interactions + link_interactions
            campaign_interactions += total_interactions
            user_dict = {
                'id': user.id,
                'name': user.name,
                'email': user.email_address,
                'phone_number': user.phone_number,
                'location_of_interest': user.location_of_interest,
                'city': user.city,
                'email_interactions': email_interactions,
                'link_interactions': link_interactions,
                'total_interactions': total_interactions
            }            
            users_for_campaign.append(user_dict)
    return users_for_campaign, campaign_interactions

def users_interactions_all_campaigns(all_users):
    '''
    Takes as input all the users and gives out the interactions user
    has ever done with any of the campaign.
    '''
    users_interaction = []
    for user in all_users:
        email_interactions, link_interactions, total_interactions = 0,0,0
        user_status = get_object_or_404(UserStatus, pk=user.id)
        for k,v in user_status.email_opens.items():
            email_interactions += v
        for k,v in user_status.email_opens.items():
            link_interactions += v
        total_interactions = email_interactions + link_interactions
        campaigns_participated_count = len(user.participated_campaigns)
        user_dict = {
            'id': user.id,
            'name': user.name,
            'email': user.email_address,
            'phone_number': user.phone_number,
            'location_of_interest': user.location_of_interest,
            'city': user.city,
            'email_interactions': email_interactions,
            'link_interactions': link_interactions,
            'total_interactions': total_interactions,
            'campaigns': campaigns_participated_count
        }
        users_interaction.append(user_dict) 
    return users_interaction

def user_hit_rates(users, campaigns):
    '''
    Takes as input a list of campaign IDS and returns the hit rate
    percentage for the user interactions.
    '''
    user_engagement_percentages = []
    total_campaigns = len(campaigns)

    for user in users:
        all_interactions = 0
        for campaign in campaigns:
            campaign_id = str(campaign.id)
            interaction_details, interactions = users_interactions_single_campaign([user], campaign_id)
            all_interactions += interactions

        percentage = ((all_interactions*0.5)/total_campaigns) * 100
        if interaction_details:
            percent_dict = {
                'user_id': interaction_details[0]['id'],
                'name': interaction_details[0]['name'],
                'email': interaction_details[0]['email'],
                'location_of_interest': interaction_details[0]['location_of_interest'],
                'hit_rate': percentage
            }
        else:
            percent_dict = {
                'user_id': user.id,
                'name': user.name,
                'email': user.email_address,
                'location_of_interest': user.location_of_interest,
                'hit_rate': 0.0
            }
        user_engagement_percentages.append(percent_dict)

    return user_engagement_percentages


def user_sms_hit_rates(users, campaigns):
    user_engagement_percentages = []
    total_campaigns = len(campaigns)

    for user in users:
        all_interactions = 0
        for campaign in campaigns:
            campaign_id = str(campaign.id)
            interaction_details, interactions = users_interactions_single_campaign([user], campaign_id)
            all_interactions += interactions

        percentage = ((all_interactions)/total_campaigns) * 100
        if interaction_details:
            percent_dict = {
                'user_id': interaction_details[0]['id'],
                'name': interaction_details[0]['name'],
                'email': interaction_details[0]['email'],
                'phone_number': interaction_details[0]['phone_number'],
                'location_of_interest': interaction_details[0]['location_of_interest'],
                'hit_rate': percentage
            }
        else:
            percent_dict = {
                'user_id': user.id,
                'name': user.name,
                'phone_number': user.phone_number,
                'location_of_interest': user.location_of_interest,
                'hit_rate': 0.0
            }
        user_engagement_percentages.append(percent_dict)

    return user_engagement_percentages