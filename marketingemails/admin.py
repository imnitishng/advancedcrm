from django.contrib import admin

from .models import User, Campaigns, UserStatus

# Register your models here.
admin.site.register(User)
admin.site.register(Campaigns)
admin.site.register(UserStatus)
