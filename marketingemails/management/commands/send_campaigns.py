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

        # ScheduledCampaign.objects.filter(scheduled_timestamp__date=dt).exclude(scheduled_timestamp__time__lte=dt-datetime.timedelta(minutes=200)).filter(scheduled_timestamp__time__lte=dt.time()).values('campaign__name')
        # dt = datetime.datetime(2020, 11, 10, 15, 6, tzinfo=pytz.UTC)
        campaign_jobs_to_deliver = ScheduledCampaign.objects.filter(
            scheduled_timestamp__lte=dt)
        # campaign_jobs_to_deliver = ScheduledCampaign.objects.filter(
        #     campaign__name='auto corr-1')
        
        if campaign_jobs_to_deliver:
            for job in campaign_jobs_to_deliver:
                deliver_campaign(job)
