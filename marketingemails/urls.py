from django.urls import path

from . import views

app_name = 'marketingemails'
urlpatterns = [
    path('', views.index, name='index'),
    path('sendmail/', views.sendmail, name='mailsent'),
    path(r'^image_load/$', views.image_load, name='image_load'),
]