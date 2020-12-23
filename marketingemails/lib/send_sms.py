import os
from urllib.parse import urljoin
import urllib.request
import urllib.parse
import json

from django.utils import timezone
from django.urls import reverse
from django.http import HttpResponse
from django.shortcuts import get_list_or_404, get_object_or_404, render, redirect
from django.core.mail import get_connection, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

from marketingemails.models import User, UserStatus, Campaigns, ScheduledCampaign
from marketingtexts.models import SMSCampaign, ScheduledSMSCampaign


def parse_campaign_users(campaign):
    user_ids = campaign.audience
    user_objects = User.objects.in_bulk(user_ids)
    
    user_ids, user_phone_numbers = [], []    
    for user_id, user in user_objects.items():
        user_ids.append(user_id)
        user_phone_numbers.append(user.phone_number)

    return user_ids, user_phone_numbers


def build_message(user_id, campaign):
    tracking_link = reverse("marketingemails:redirect_to_yor", 
        args=(str(campaign.id), str(user_id)))

    domain_name = settings.SERVER_IP
    marketing_url = urljoin(domain_name, tracking_link)

    if campaign.campaign_type == 1:
        text_content = f"Hello, Here are some properties in you might be interested in {marketing_url}."
    elif campaign.campaign_type == 2:
        text_content = f"Interested in buying new property?  Here are some might like {marketing_url}."
    elif campaign.campaign_type == 3:
        text_content = f"Interested in buying new property?  Here are some might like {marketing_url}."
    elif campaign.campaign_type == 99:
        text_content = f"Hello, Here are some properties in you might be interested in {marketing_url}."
    else:
        text_content = f"Some YOR properties for you, have a look here {marketing_url}."
    return text_content


def fix_phno_format(phone_number):
    number10Digit = phone_number[-10:]
    if len(number10Digit) == 10:
        return '91' + number10Digit
    else:
        return None


def create_text_messages(user_ids, phone_numbers, campaign):
    message_data = []
    for ID, number in zip(user_ids, phone_numbers):
        formatted_number = fix_phno_format(number)
        if formatted_number:
            message_data.append({
                'number': formatted_number,
                'text': build_message(ID, campaign)
            })
        else:
            continue
    return message_data


def send_campaign_sms(campaign):
    user_ids, phone_numbers = parse_campaign_users(campaign)
    message_data = create_text_messages(user_ids, phone_numbers, campaign)

    # Data is sent partially since API only accepts 500 entries at a time
    apikey = settings.API_KEY
    atLeast1Sent = 0
    for i in range(0, len(message_data), 498):
        if i+498 < len(message_data)-1:
            partial_message_data = message_data[i:i+498]
        else:
            partial_message_data = message_data[i:]

        final_message = {
            'sender': '226584',
            'messages': partial_message_data
        }
        json_messages = json.dumps(final_message)
        data =  urllib.parse.urlencode({
            'apikey': apikey, 
            'data': json_messages,
            'test': False
        })
        data = data.encode('utf-8')

        request = urllib.request.Request("https://api.textlocal.in/bulk_json")
        f = urllib.request.urlopen(request, data)
        response_text = f.read()
        response = json.loads(response_text)

        if response.get('balance_pre_send') == response.get('balance_post_send'):
            # No messages were sent because of time regulations
            return False
        else:
            atLeast1Sent = 1
    
    if atLeast1Sent:
        return True
    return False

        