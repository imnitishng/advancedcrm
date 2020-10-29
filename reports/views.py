from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse
from django.shortcuts import get_list_or_404, get_object_or_404, render, redirect
from django.core.mail import get_connection, EmailMultiAlternatives
from django.template.loader import render_to_string

from marketingemails.models import User, UserStatus, Campaigns
from .utils import users_interactions_single_campaign, users_interactions_all_campaigns


def index(request):
    return render(request, 'reports/index.html')


def campaigns(request):
    successful_campaigns = Campaigns.objects.all()
    context = {
        'campaigns': successful_campaigns
    }
    return render(request, 'reports/campaigns.html', {'campaigns': successful_campaigns})


def single_campaign_report(request, campaign_id):
    campaign = get_object_or_404(Campaigns, pk=campaign_id)
    
    # Get all users and filter the ones for this campaign
    all_users = User.objects.all()
    users_for_campaign, campaign_interactions = users_interactions_single_campaign(all_users, campaign_id)
    extras = {
        'campaign_interactions': campaign_interactions
    }

    return render(request, 'reports/campaign_report.html', 
        {'users': users_for_campaign, 'campaign': campaign, 'extras': extras})

    
def audience(request):
    users = User.objects.all()
    users_status = UserStatus.objects.all()
    users_interaction = users_interactions_all_campaigns(users)
    return render(request, 'reports/audience.html', {'users': users_interaction})


def single_user_view(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user_status = get_object_or_404(UserStatus, pk=user_id)
    user_campaign_dict = {}
    for campaign_id in user.participated_campaigns:
        campaign = get_object_or_404(Campaigns, pk=campaign_id)
        campaign_dict = {
            'name': campaign.name,
            'email_opens': user_status.email_opens.get(campaign_id),
            'link_opens': user_status.link_opens.get(campaign_id)
        } 
        user_campaign_dict[campaign_id] = campaign_dict    

    return render(request, 'reports/single_user.html', {'user': user, 'campaigns': user_campaign_dict})


def micromarkets(request):
    users = User.objects.all()
    user_interactions = users_interactions_all_campaigns(users)
    city_map, subregion_map, subregion_to_city = {}, {}, {}
    
    for interaction in user_interactions:
        if interaction['location_of_interest'] not in subregion_to_city:
            subregion_to_city[interaction['location_of_interest']] = interaction['city']

        if interaction['location_of_interest'] in subregion_map:
            subregion_map[interaction['location_of_interest']] += interaction['total_interactions']
        else:
            subregion_map[interaction['location_of_interest']] = interaction['total_interactions']

        if interaction['city'] in city_map:
            city_map[interaction['city']] += interaction['total_interactions']
        else:
            city_map[interaction['city']] = interaction['total_interactions']

    final_subregions = []
    for k, v in subregion_map.items():
        final_subregions.append({'subregion': k, 'city': subregion_to_city.get(k, 'NULL'), 'impressions': v})

    return render(request, 'reports/micromarkets.html', {'cities': city_map, 'subregions': final_subregions})
        

def single_micromarket(request, subregion):
    users_for_location = User.objects.filter(location_of_interest=subregion)
    users_interaction = users_interactions_all_campaigns(users_for_location)
    return render(request, 'reports/single_location.html', {'users': users_interaction, 'subregion': subregion})