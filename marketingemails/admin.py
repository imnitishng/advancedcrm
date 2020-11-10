from django.contrib import admin

from .models import User, Campaigns, UserStatus, ScheduledCampaign


class CampaignsAdmin(admin.ModelAdmin):
    list_display = ('name', 'trigger_time', 'parent_campaigns', 'future_campaigns')

    def trigger_time(self, obj):
        return f"{obj.launch_datetime.strftime('%d, %b %Y - %I:%M%p')}"
    trigger_time.short_description = 'Trigger Time'
    

admin.site.register(User)
admin.site.register(Campaigns, CampaignsAdmin)
admin.site.register(UserStatus)
admin.site.register(ScheduledCampaign)
