import os
from django.utils import timezone

from django.urls import reverse
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_list_or_404, get_object_or_404, render, redirect
from django.core.mail import get_connection, EmailMultiAlternatives
from django.template.loader import render_to_string
from PIL import Image

from marketingemails.models import User, UserStatus
from marketingemails.forms import UserListForm, UserListModelForm
from marketingemails.utils import dictionary_to_str
from marketingemails.lib.automatic_campaigns import schedule_future_campaign
from marketingemails.lib.send_mail import send_mass_html_mail, get_mail_data
from marketingemails.lib.send_sms import update_user_status

from .models import SMSCampaign, ScheduledSMSCampaign


def create(request):
    users = get_list_or_404(User, phone_number__isnull=False)
    return render(request, 'marketingtexts/create_sms_campaign.html', {'users': users[:100]})


def audience_select(request):
    '''
    Save the campaign and select audience for the same.
    '''
    campaign = SMSCampaign(
        name = request.POST.get('campaign_name'),
        description = request.POST.get('campaign_desc'),
        creation_date = timezone.now(),
        launch_datetime = timezone.now()
    )
    campaign.save()
    request.session['campaign_id'] = str(campaign.id)
    request.session['future_campaigns_count'] = request.POST.get('auto_campaigns_count')    
    # users = get_list_or_404(User, phone_number__isnull=False)
    users = User.objects.filter(phone_number__isnull=False).exclude(phone_number='')
    return render(request, 'marketingtexts/audience_select.html', {'users': users[:100], 'campaign': campaign})


def sendsms(request):
    if request.POST.get('select_all_users'):
        user_pkids = list(User.objects.filter(phone_number__isnull=False).exclude(phone_number='').values_list('id', flat=True))
    elif request.POST.get('start_idx', None) or request.POST.get('last_idx', None):
        start_idx = int(request.POST.get('start_idx'))
        last_idx = int(request.POST.get('last_idx'))
        user_pkids = list(User.objects.filter(phone_number__isnull=False).exclude(phone_number='').values_list('id', flat=True))

        if last_idx <= start_idx or last_idx >= len(user_pkids) or start_idx >= len(user_pkids):
            return HttpResponseBadRequest('Index was not properly specified. Try Again')
        else:
            user_pkids = user_pkids[start_idx:last_idx]
    else:
        user_pkids = request.POST.getlist('user_selected')
    
    # Save selected audience to the campaign
    campaign_id = request.session['campaign_id']
    future_campaigns_count = request.session['future_campaigns_count']

    campaign = get_object_or_404(SMSCampaign, pk=campaign_id)
    campaign.audience = user_pkids
    campaign.save()

    # Add dummy future campaigns and queue them to be sent
    schedule_future_campaign(future_campaigns_count, user_pkids, campaign, 'sms')
    scheduled_current_campaign = ScheduledSMSCampaign(
        scheduled_timestamp = timezone.now(),
        campaign = campaign
    )
    scheduled_current_campaign.save()
    
    return render(request, 'marketingtexts/smssent.html')
