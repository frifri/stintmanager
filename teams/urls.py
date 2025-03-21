from django.urls import path
from . import views

app_name = 'teams'

urlpatterns = [
    path('dashboard/', views.team_list, name='dashboard'),

    # Team management
    path('create/', views.team_create, name='create'),
    path('<uuid:pk>/', views.team_detail, name='detail'),
    path('<uuid:pk>/edit/', views.team_edit, name='edit'),
    path('<uuid:pk>/delete/', views.team_delete, name='delete'),  # Add this line
    path('race/<uuid:race_id>/create/', views.create_for_race, name='create_for_race'),
    path('<uuid:team_id>/members/add/', views.add_member, name='add_member'),
    path('membership/<uuid:membership_id>/remove/', views.remove_member, name='remove_member'),
    path('<uuid:team_id>/join/', views.join_team, name='join_team'),

    path('race/<uuid:race_id>/', views.race_teams, name='race_teams'),
]