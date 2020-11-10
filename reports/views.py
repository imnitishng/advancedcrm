from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse
from django.shortcuts import get_list_or_404, get_object_or_404, render, redirect
from django.core.mail import get_connection, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.timezone import now as timezone_now

from marketingemails.models import User, UserStatus, Campaigns
from .utils import users_interactions_single_campaign, users_interactions_all_campaigns, user_hit_rates


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


def campaign_series(request):
    parent_campaigns = Campaigns.objects.exclude(future_campaigns='').filter(parent_campaigns='')
    context = {
        'campaigns': parent_campaigns
    }
    return render(request, 'reports/parent_campaigns.html', {'campaigns': parent_campaigns})


def single_campaign_series(request, parent_campaign_id):
    parent_campaign = get_object_or_404(Campaigns, pk=parent_campaign_id)
    child_campaign_ids = parent_campaign.future_campaigns

    campaigns_sent = []
    campaigns_pending = []
    for id in child_campaign_ids:
        child = Campaigns.objects.filter(pk=id, launch_datetime__lte = timezone_now())
        if child:
            campaigns_sent.append(Campaigns.objects.get(pk=id))
        else:
            campaigns_pending.append(Campaigns.objects.get(pk=id))
    
    campaigns_sent.append(parent_campaign)
    if campaigns_sent:
        parent_campaign_user_ids = parent_campaign.audience
        parent_campaign_users = User.objects.in_bulk(parent_campaign_user_ids)
        if parent_campaign_users:
            parent_campaign_users = list(parent_campaign_users.values())

        hitrate_percentages = user_hit_rates(parent_campaign_users, campaigns_sent)
        return render(request, 'reports/single_campaign_series.html', {
            'hitrates': hitrate_percentages, 
            'campaign': parent_campaign, 
            'childs_sent': campaigns_sent,
            'childs_pending': campaigns_pending})
    else:
        return render(request, 'reports/null_series.html', {'childs_pending': campaigns_pending})
