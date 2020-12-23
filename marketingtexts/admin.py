from django.contrib import admin

from .models import SMSCampaign, ScheduledSMSCampaign


class SMSCampaignsAdmin(admin.ModelAdmin):
    list_display = ('name', 'trigger_time', 'parent_campaigns', 'future_campaigns')

    def trigger_time(self, obj):
        return f"{obj.launch_datetime.strftime('%d, %b %Y - %I:%M%p')}"
    trigger_time.short_description = 'Trigger Time'


admin.site.register(SMSCampaign, SMSCampaignsAdmin)
admin.site.register(ScheduledSMSCampaign)