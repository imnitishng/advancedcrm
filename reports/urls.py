from django.urls import path

from . import views

app_name = 'reports'
urlpatterns = [
    path('', views.index, name='index'),
    path('campaigns/', views.campaigns, name='campaigns'),
    path('campaigns/<str:campaign_id>', views.single_campaign_report, name='single_campaign_report'),
    path('audience/', views.audience, name='audience'),
    path('audience/<str:user_id>', views.single_user_view, name='single_user_report'),
    path('micromarkets/', views.micromarkets, name='micromarkets')
]

# urlpatterns = [
#     path('<page_slug>-<page_id>/', include([
#         path('history/', views.history),
#         path('edit/', views.edit),
#         path('discuss/', views.discuss),
#         path('permissions/', views.permissions),
#     ])),
# ]