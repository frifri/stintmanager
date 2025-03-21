from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from races.models import Race, RaceDriver
from .models import Team, TeamMembership
from .forms import TeamForm
from core.models import User


@login_required
def team_detail(request, pk):
    """View detailed information about a specific team."""
    team = get_object_or_404(Team.objects.select_related('owner'), pk=pk)
    
    # Get all memberships for this team
    memberships = TeamMembership.objects.filter(team=team).select_related('user')
    
    # Get race entry for this team
    race = team.race

    # Check if the user is a member of this team
    is_member = team.memberships.filter(user=request.user).exists()
    
    # Check permissions
    is_owner = team.owner == request.user
    
    # Find races the team could enter
    available_races = Race.objects.exclude(
        team_entries__team=team
    ).filter(
        start_time__gt=timezone.now()  # Only future races
    ).order_by('start_time')
    
    context = {
        'team': team,
        'memberships': memberships,
        'race': race,
        'is_member': is_member,
        'is_owner': is_owner,
        'available_races': available_races,
    }
    return render(request, 'teams/team_detail.html', context)

@login_required
def team_list(request):
    """View all teams the user owns or is a member of"""
    # Teams owned by the user
    owned_teams = Team.objects.filter(owner=request.user)

    # Teams the user is a member of but does not own
    member_teams = Team.objects.filter(
        memberships__user=request.user
    ).exclude(
        owner=request.user
    )

    context = {
        'owned_teams': owned_teams,
        'member_teams': member_teams,
    }
    return render(request, 'teams/team_list.html', context)

@login_required
def team_edit(request, pk):
    team = get_object_or_404(Team, pk=pk)
    race = team.race
    
    # Check permissions
    if team.owner != request.user and race.created_by != request.user:
        messages.error(request, "You don't have permission to edit this team.")
        return redirect('teams:detail', pk=team.pk)
    
    if request.method == 'POST':
        form = TeamForm(request.POST, instance=team)
        if form.is_valid():
            form.save()
            messages.success(request, f'Team "{team.name}" updated successfully!')
            return redirect('teams:detail', pk=team.pk)
    else:
        form = TeamForm(instance=team)
    
    return render(request, 'teams/team_form.html', {
        'form': form,
        'race': race,
        'team': team,
        'title': 'Edit Team',
        'is_edit': True
    })


@login_required
def team_delete(request, pk):
    team = get_object_or_404(Team, pk=pk)
    race = team.race
    
    # Check permissions
    if team.owner != request.user and race.created_by != request.user:
        messages.error(request, "You don't have permission to delete this team.")
        return redirect('teams:detail', pk=team.pk)
    
    if request.method == 'POST':
        team_name = team.name
        race_id = race.pk
        team.delete()
        messages.success(request, f'Team "{team_name}" deleted successfully!')
        return redirect('teams:list', race_id=race_id)
    
    return redirect('teams:detail', pk=team.pk)


@login_required
def add_member(request, team_id):
    """Add a member to a team"""
    team = get_object_or_404(Team, pk=team_id)
    
    # Check permissions
    if team.owner != request.user:
        messages.error(request, "Only the team owner can add members.")
        return redirect('teams:detail', pk=team.pk)
    
    if request.method == 'POST':
        user_email = request.POST.get('user_email')
        role = request.POST.get('role', 'Driver')
        
        try:
            user = User.objects.get(email=user_email)
            
            # Check if user is already in this team
            if TeamMembership.objects.filter(team=team, user=user).exists():
                messages.warning(request, f"{user.get_full_name()} is already in this team.")
            else:
                TeamMembership.objects.create(
                    team=team,
                    user=user,
                    role=role
                )
                messages.success(
                    request, 
                    f"{user.get_full_name()} added to {team.name} as {role}."
                )
        except User.DoesNotExist:
            messages.error(request, f"No user found with email {user_email}.")
        
        return redirect('teams:detail', pk=team.pk)
    
    return redirect('teams:detail', pk=team.pk)


@login_required
def remove_member(request, membership_id):
    membership = get_object_or_404(
        TeamMembership.objects.select_related('team', 'driver__user', 'team__race'),
        pk=membership_id
    )
    team = membership.team
    race = team.race
    
    # Check permissions
    if (team.owner != request.user and 
        race.created_by != request.user and 
        membership.driver.user != request.user):
        messages.error(request, "You don't have permission to remove this team member.")
        return redirect('teams:detail', pk=team.pk)
    
    if request.method == 'POST':
        driver_name = membership.driver.user.get_full_name()
        membership.delete()
        messages.success(request, f"{driver_name} removed from {team.name}.")
        return redirect('teams:detail', pk=team.pk)
    
    return redirect('teams:detail', pk=team.pk)


@login_required
def join_team(request, team_id):
    """Join a team for a race"""
    team = get_object_or_404(Team, pk=team_id)
    race = team.race
    
    # Check if user is a driver in this race
    user_driver = get_object_or_404(RaceDriver, race=race, user=request.user)
    
    # Check if already in the team
    if TeamMembership.objects.filter(team=team, user=request.user).exists():
        messages.info(request, f"You're already a member of {team.name}.")
        return redirect('races:detail', pk=race.pk)
    
    if request.method == 'POST':
        # Add the user to the team
        TeamMembership.objects.create(
            team=team,
            user=request.user,
            role='Driver'  # Default role
        )
        messages.success(request, f"You've joined {team.name}!")
        return redirect('races:detail', pk=race.pk)
    
    return redirect('races:detail', pk=race.pk)


@login_required
def team_dashboard(request):
    """Dashboard showing all teams the user is involved with."""
    # Teams the user owns
    owned_teams = Team.objects.filter(owner=request.user).select_related('race')
    
    # Teams the user is a member of (but doesn't own)
    user_drivers = RaceDriver.objects.filter(user=request.user)
    member_teams = Team.objects.filter(
        memberships__driver__in=user_drivers
    ).exclude(
        owner=request.user  # Exclude teams the user owns to avoid duplication
    ).select_related('race').distinct()
    
    # Races where the user is a driver but hasn't joined a team
    races_without_teams = Race.objects.filter(
        drivers__user=request.user
    ).exclude(
        id__in=owned_teams.values_list('race_id', flat=True)
    ).exclude(
        id__in=member_teams.values_list('race_id', flat=True)
    ).distinct()
    
    context = {
        'owned_teams': owned_teams,
        'member_teams': member_teams,
        'races_without_teams': races_without_teams,
    }
    return render(request, 'teams/team_dashboard.html', context)

@login_required
def team_create(request):
    """Create a new team"""
    if request.method == 'POST':
        form = TeamForm(request.POST)
        if form.is_valid():
            team = form.save(commit=False)
            team.owner = request.user
            team.save()
            
            # Automatically add creator as a team member with "Team Manager" role
            TeamMembership.objects.create(
                team=team,
                user=request.user,
                role='Team Manager'
            )
            
            messages.success(request, f'Team "{team.name}" created successfully!')
            return redirect('teams:detail', pk=team.pk)
    else:
        form = TeamForm()
    
    return render(request, 'teams/team_form.html', {
        'form': form, 
        'title': 'Create Team'
    })

@login_required
def race_teams(request, race_id):
    """View teams participating in a specific race"""
    race = get_object_or_404(Race, pk=race_id)
    teams = Team.objects.filter(
        race_entries__race=race
    ).select_related('owner').prefetch_related('memberships')
    
    # Check if user is the race creator
    is_creator = race.created_by == request.user
    
    context = {
        'race': race,
        'teams': teams,
        'is_creator': is_creator,
    }
    return render(request, 'teams/race_teams.html', context)


@login_required
def create_for_race(request, race_id):
    """Create a team for a specific race"""
    race = get_object_or_404(Race, pk=race_id)
    
    # Check if user is allowed to create a team for this race
    if race.created_by != request.user:
        messages.error(request, "Only the race organizer can create a team.")
        return redirect('races:detail', pk=race.pk)
    
    # Check if race already has a team
    try:
        team = race.team
        messages.warning(request, f"This race already has a team: {team.name}")
        return redirect('races:detail', pk=race.pk)
    except Team.DoesNotExist:
        pass
    
    if request.method == 'POST':
        form = TeamForm(request.POST)
        if form.is_valid():
            team = form.save(commit=False)
            team.race = race
            team.owner = request.user
            team.save()
            
            # Automatically add creator as a team member
            TeamMembership.objects.create(
                team=team,
                user=request.user,
                role='Team Manager'
            )
            
            messages.success(request, f'Team "{team.name}" created successfully!')
            return redirect('races:detail', pk=race.pk)
    else:
        # Pre-fill with race name as default team name
        form = TeamForm(initial={'name': f"{race.name} Team"})
    
    return render(request, 'teams/team_form.html', {
        'form': form,
        'race': race,
        'title': 'Create Team for Race'
    })