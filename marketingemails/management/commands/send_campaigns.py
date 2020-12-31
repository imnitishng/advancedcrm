import datetime
import time
import pytz

from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import now as timezone_now

from marketingemails.models import ScheduledCampaign
from marketingemails.lib.automatic_campaigns import deliver_campaign

class Command(BaseCommand):
    help = 'Send the scheduled campaigns'

    def handle(self, *args, **options):

        dt = timezone_now()
        campaign_jobs_to_deliver = ScheduledCampaign.objects.filter(
            scheduled_timestamp__lte=dt)
        
        if campaign_jobs_to_deliver:
            i = 0
            for job in campaign_jobs_to_deliver:
                deliver_campaign(job, 'email')
                i += 1
            print(f'Sent {i} emails! Exiting.')
        else:
            print('oof nothing to send! F')
