from django.urls import path
from . import views

app_name = 'teams'

urlpatterns = [
    path('dashboard/', views.team_list, name='dashboard'),

    # Team management
    path('<uuid:pk>/', views.team_detail, name='detail'),
    path('<uuid:pk>/edit/', views.team_edit, name='edit'),
    path('race/<uuid:race_id>/create/', views.create_for_race, name='create_for_race'),
    path('<uuid:team_id>/members/add/', views.add_member, name='add_member'),
    path('membership/<uuid:membership_id>/remove/', views.remove_member, name='remove_member'),
    path('<uuid:team_id>/join/', views.join_team, name='join_team'),
    
    # Race entries
    path('<uuid:team_id>/races/enter/', views.enter_race, name='enter_race'),
    path('entry/<uuid:entry_id>/withdraw/', views.withdraw_from_race, name='withdraw'),

    path('race/<uuid:race_id>/', views.race_teams, name='race_teams'),
]