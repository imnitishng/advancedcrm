import os
from urllib.parse import urljoin

from django.utils import timezone
from django.urls import reverse
from django.http import HttpResponse
from django.shortcuts import get_list_or_404, get_object_or_404, render, redirect
from django.core.mail import get_connection, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

from marketingemails.models import User, UserStatus, Campaigns, ScheduledCampaign


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


def select_email_type(campaign, user, context):
    '''
    Select HTML Email to send based on the campaign type.
    '''
    user_first_name = user.name.split(' ')[0]
    if campaign.campaign_type == 1:
        subject = f"Hi {user_first_name}! Have a look at some properties on YourOwnRoom."
        html_content = render_to_string('mails/campaign1.html', {'context': context})
    elif campaign.campaign_type == 2:
        subject = f"Hi {user_first_name}! Here are some handpicked recommendations for you."
        html_content = render_to_string('mails/campaign2.html', {'context': context})
    elif campaign.campaign_type == 3:
        subject = f"Hi {user_first_name}! Here are some handpicked recommendations for you."
        html_content = render_to_string('mails/campaign3.html', {'context': context})
    elif campaign.campaign_type == 99:
        subject = "Seems like you're lost"
        html_content = render_to_string('mails/remarketing_campaign.html', {'context': context})
    else:
        subject = "YourOwnRoom recommendations"
        html_content = render_to_string('mails/campaign1.html', {'context': context})
    
    return subject, html_content


def build_email(user, campaign, request):
    campaign_id = str(campaign.id)

    text_content = f"""
        Hi {user.name},\n\n
        Here are some properties in {user.location_of_interest} you might be interested in,
        {user.marketing_link}.
        """

    reverse_image_url = reverse("marketingemails:image_load", 
        args=(str(campaign_id), str(user.id)))
    reverse_marketing_url = reverse("marketingemails:redirect_to_yor", 
        args=(str(campaign_id), str(user.id)))
    
    if request:
        image_url = request.build_absolute_uri(reverse_image_url)
        marketing_url = request.build_absolute_uri(reverse_marketing_url)
    else:
        domain_name = settings.SERVER_IP
        image_url = urljoin(domain_name, reverse_image_url)
        marketing_url = urljoin(domain_name, reverse_marketing_url)

    context = {
        'name': user.name,
        'location': user.location_of_interest,
        'image_url': image_url,
        'link': marketing_url
    }

    subject, html_content = select_email_type(campaign, user, context) 
    return subject, text_content, html_content


def get_mail_data(user_pkids, campaign, request):
    users_to_mail_data = []
    campaign_id = str(campaign.id)

    # For every user, initialise user parameters, build and send the email
    for user_id in user_pkids:
        user = get_object_or_404(User, pk=user_id)
        if user.participated_campaigns[0] == '':
            user.participated_campaigns = [campaign_id]
        else:
            user.participated_campaigns.append(campaign_id)
        user.save()
        
        try:
            get_object_or_404(UserStatus, pk=user_id)
        except:
            user = get_object_or_404(User, pk=user_id)
            # campaign_status_empty_dict = {campaign_id: 0}
            new_user_status = UserStatus(
                user=user
            )
            new_user_status.save()

        subject, text_mail, html_mail = build_email(user, campaign, request)
        users_to_mail_data.append((subject, text_mail, html_mail, 'imnitish.ng@gmail.com', user.email_address))
    
    return users_to_mail_data


def send_campaign_mails(campaign):
    users = campaign.audience
    if users:
        users_to_mail_data = get_mail_data(users, campaign, None)
        send_mass_html_mail(users_to_mail_data)