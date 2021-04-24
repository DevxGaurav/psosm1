from django.urls import path

from You_V2_server import views

urlpatterns = [
    path('', views.index),
    path('personality', views.personality)
]