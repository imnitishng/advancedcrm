from django.urls import path

from . import views

app_name = 'reports'
urlpatterns = [
    path('', views.index, name='index'),

    # EMAIL REPORTS
    path('campaigns/', views.campaigns, name='campaigns'),
    path('campaigns/<str:campaign_id>', views.single_campaign_report, name='single_campaign_report'),
    path('campaign_series/', views.campaign_series, name='campaign_series'),
    path('campaign_series/<str:parent_campaign_id>', views.single_campaign_series, name='single_campaign_series'),

    # SMS REPORTS
    path('sms_campaigns/', views.sms_campaigns, name='sms_campaigns'),
    path('sms_campaigns/<str:campaign_id>', views.single_sms_campaign_report, name='single_sms_campaign_report'),
    path('sms_campaign_series/', views.sms_campaign_series, name='sms_campaign_series'),
    path('sms_campaign_series/<str:parent_campaign_id>', views.single_sms_campaign_series, name='single_sms_campaign_series'),

    # USER REPORTS
    path('audience/', views.audience, name='audience'),
    path('audience/<str:user_id>', views.single_user_view, name='single_user_report'),
    path('micromarkets/', views.micromarkets, name='micromarkets'),
    path('micromarkets/<str:subregion>', views.single_micromarket, name='single_micromarket'),
]
