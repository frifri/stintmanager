from django.urls import path
from . import views

app_name = 'races'

urlpatterns = [
    path('', views.race_list, name='list'),
    path('create/', views.race_create, name='create'),
    path('<uuid:pk>/', views.race_detail, name='detail'),
    path('<uuid:pk>/edit/', views.race_edit, name='edit'),
    path('<uuid:pk>/delete/', views.race_delete, name='delete'),
]
