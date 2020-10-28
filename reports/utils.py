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
                'name': user.name,
                'email': user.email_address,
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
    Takes as input all the users and gives ou the interactions user
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
            'location_of_interest': user.location_of_interest,
            'city': user.city,
            'email_interactions': email_interactions,
            'link_interactions': link_interactions,
            'total_interactions': total_interactions,
            'campaigns': campaigns_participated_count
        }
        users_interaction.append(user_dict) 
    return users_interaction
