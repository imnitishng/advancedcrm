import datetime
import math

from django.core.mail import get_connection, EmailMultiAlternatives
from django.utils.timezone import now as timezone_now

from .models import User, UserStatus, Campaigns, ScheduledCampaign


def dictionary_to_str(dic):
    pass

        