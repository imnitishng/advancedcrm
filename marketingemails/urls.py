from django.urls import path

from . import views

app_name = 'marketingemails'
urlpatterns = [
    path('', views.index, name='index'),
    path('sendmail/', views.sendmail, name='mailsent'),
    path('audience_select/', views.audience_select, name='audience_select'),
    path('image_load/<str:campaign_id>/<str:user_id>', views.image_load, name='image_load'),
    path('redirect/<str:campaign_id>/<str:user_id>', views.redirect_yor, name='redirect_to_yor'),
]