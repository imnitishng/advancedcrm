import os
from django.utils import timezone

from django.urls import reverse
from django.http import HttpResponse
from django.shortcuts import get_list_or_404, get_object_or_404, render, redirect
from django.core.mail import get_connection, EmailMultiAlternatives
from django.template.loader import render_to_string
from PIL import Image

from .models import User, UserStatus, Campaigns, ScheduledCampaign
from .forms import UserListForm, UserListModelForm
from .utils import dictionary_to_str
from .lib.automatic_campaigns import schedule_future_campaign
from .lib.send_mail import send_mass_html_mail, get_mail_data


def index(request):
    return render(request, 'marketingemails/index.html')


def create(request):
    '''
    Renders basic form to create a campaign and configure campaign related options.
    '''
    users = get_list_or_404(User, email_address__isnull=False)
    return render(request, 'marketingemails/create_campaign.html', {'users': users[:100]})


def sendmail(request):
    '''
    Renders the campaign success page after dispatching a campaign.
    The request recieved stores information about users selected, these users are fetched and 
    the camapaign is scheduled to be triggered.
    '''
    if request.POST.get('select_all_users'):
        user_pkids = list(User.objects.filter(email_address__isnull=False).exclude(email_address='').values_list('id', flat=True))
    elif request.POST.get('start_idx', None) or request.POST.get('last_idx', None):
        start_idx = int(request.POST.get('start_idx'))
        last_idx = int(request.POST.get('last_idx'))
        user_pkids = list(User.objects.filter(email_address__isnull=False).exclude(email_address='').values_list('id', flat=True))

        if last_idx <= start_idx or last_idx > len(user_pkids) or start_idx >= len(user_pkids) or len(user_pkids) == 0:
            return HttpResponseBadRequest('Index was not properly specified. Try Again')
        else:
            user_pkids = user_pkids[start_idx:last_idx]
    else:
        user_pkids = request.POST.getlist('user_selected')
    
    # Save selected audience to the campaign
    campaign_id = request.session['campaign_id']
    future_campaigns_count = request.session['future_campaigns_count']

    campaign = get_object_or_404(Campaigns, pk=campaign_id)
    campaign.audience = user_pkids
    campaign.save()

    # Add dummy future campaigns and queue them to be sent
    schedule_future_campaign(future_campaigns_count, user_pkids, campaign, 'emails')
    scheduled_current_campaign = ScheduledCampaign(
        scheduled_timestamp = timezone.now(),
        campaign=campaign
    )
    scheduled_current_campaign.save()

    return render(request, 'marketingemails/testmailsent.html')


def audience_select(request):
    '''
    Save the campaign and select audience for the same.    
    '''
    campaign = Campaigns(
        name = request.POST.get('campaign_name'),
        description = request.POST.get('campaign_desc'),
        creation_date = timezone.now(),
        launch_datetime = timezone.now()
    )
    campaign.save()
    request.session['campaign_id'] = str(campaign.id)
    request.session['future_campaigns_count'] = request.POST.get('auto_campaigns_count')
    
    users = User.objects.filter(email_address__isnull=False).exclude(email_address='')
    return render(request, 'marketingemails/audience_select.html', 
        {'users': users[:100], 'campaign': campaign, 'valid_users': len(users)})


def image_load(request, campaign_id, user_id):
    '''
    `image_load` view is responsible for validating if an email is opened 
    or not, as soon as the URI for this view is called, the entry in our 
    database is updated and a single 1x1 pixel is sent to the email as a 
    PNG image response. If the image is loaded it signifies that the user
    has opened the email.

    Input: 
    campaign_id: Campaign for which the user has opened the email
    user_id: The user who has opened the email
    '''    
    user = get_object_or_404(UserStatus, pk=user_id)
    if user.email_opens.get(campaign_id, None):
        user.email_opens[campaign_id] += 1
    else:
        user.email_opens[campaign_id] = 1
    user.save()

    # Single pixel for email open flag
    print("\nImage Loaded\n")    
    red = Image.new('RGB', (1, 1))
    response = HttpResponse(content_type="image/png")
    red.save(response, "PNG")
    
    return response


def redirect_yor(request, campaign_id, user_id):
    '''
    Takes as input the embed link sent to user in the
    email, when the user clicks that link it is registered
    here and then the user is redirected to the desired link.

    Input: 
    campaign_id: Campaign for which the user has opened the email
    user_id: The user who has opened the email
    '''
    user = get_object_or_404(UserStatus, pk=user_id)
    if user.link_opens.get(campaign_id, None):
        user.link_opens[campaign_id] += 1
    else:
        user.link_opens[campaign_id] = 1
    user.save()

    redirect_url = user.user.marketing_link
    return redirect(redirect_url)