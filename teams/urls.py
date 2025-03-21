from django.urls import path
from . import views

app_name = 'teams'

urlpatterns = [
    path('race/<uuid:race_id>/teams/', views.team_list, name='list'),
    path('race/<uuid:race_id>/teams/create/', views.team_create, name='create'),
    path('teams/<uuid:pk>/', views.team_detail, name='detail'),
    path('teams/<uuid:pk>/edit/', views.team_edit, name='edit'),
    path('teams/<uuid:pk>/delete/', views.team_delete, name='delete'),
    path('teams/<uuid:team_id>/add-member/', views.add_member, name='add_member'),
    path('teams/membership/<uuid:membership_id>/remove/', views.remove_member, name='remove_member'),
    path('teams/<uuid:team_id>/join/', views.join_team, name='join'),
]