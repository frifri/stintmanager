from django.urls import path
from . import views

app_name = 'races'

urlpatterns = [
    path('', views.race_list, name='list'),
    path('create/', views.race_create, name='create'),
]
