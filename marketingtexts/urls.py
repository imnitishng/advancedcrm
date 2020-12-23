from django.urls import path

from . import views

app_name = 'marketingtexts'
urlpatterns = [
    path('create/', views.create, name='create'),
    path('audience_select/', views.audience_select, name='audience_select'),
    path('sendsms/', views.sendsms, name='smssent'),
    # path('image_load/<str:campaign_id>/<str:user_id>', views.image_load, name='image_load'),
    # path('redirect/<str:campaign_id>/<str:user_id>', views.redirect_yor, name='redirect_to_yor'),
]