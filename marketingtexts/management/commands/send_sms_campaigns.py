import datetime
import time
import pytz

from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import now as timezone_now

from marketingtexts.models import ScheduledSMSCampaign
from marketingemails.lib.automatic_campaigns import deliver_campaign

class Command(BaseCommand):
    help = 'Send the scheduled SMS campaigns'

    def handle(self, *args, **options):

        dt = timezone_now()
        campaign_jobs_to_deliver = ScheduledSMSCampaign.objects.filter(
            scheduled_timestamp__lte=dt)
        
        if campaign_jobs_to_deliver:
            i = 0
            for job in campaign_jobs_to_deliver:
                deliver_campaign(job, 'sms')
                i += 1
            print(f'Sent {i} SMS campaigns! Exiting.')
        else:
            print('oof nothing to send! F')
