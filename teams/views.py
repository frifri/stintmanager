from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from races.models import Race, RaceDriver
from .models import Team, TeamMembership
from .forms import TeamForm, TeamMembershipForm


@login_required
def team_list(request, race_id):
    race = get_object_or_404(Race, pk=race_id)
    teams = Team.objects.filter(race=race).prefetch_related('memberships__driver__user')
    
    # Check if user is a driver in this race
    is_driver = RaceDriver.objects.filter(race=race, user=request.user).exists()
    
    # Check if user is the race creator
    is_creator = race.created_by == request.user
    
    context = {
        'race': race,
        'teams': teams,
        'is_driver': is_driver,
        'is_creator': is_creator,
    }
    return render(request, 'teams/team_list.html', context)


@login_required
def team_create(request, race_id):
    race = get_object_or_404(Race, pk=race_id)
    
    # Only race creator can create teams
    if race.created_by != request.user:
        messages.error(request, "Only the race organizer can create teams.")
        return redirect('races:detail', pk=race.pk)
    
    if request.method == 'POST':
        form = TeamForm(request.POST)
        if form.is_valid():
            team = form.save(commit=False)
            team.race = race
            team.owner = request.user
            team.save()
            messages.success(request, f'Team "{team.name}" created successfully!')
            return redirect('teams:list', race_id=race.pk)
    else:
        form = TeamForm()
    
    return render(request, 'teams/team_form.html', {
        'form': form,
        'race': race,
        'title': 'Create Team'
    })


@login_required
def team_detail(request, pk):
    team = get_object_or_404(Team.objects.select_related('race', 'owner'), pk=pk)
    race = team.race
    
    # Get all memberships for this team
    memberships = TeamMembership.objects.filter(team=team).select_related('driver__user')
    
    # Get drivers in the race who are not yet in this team
    available_drivers = RaceDriver.objects.filter(
        race=race
    ).exclude(
        team_memberships__team=team
    ).select_related('user')
    
    # Check permissions
    is_owner = team.owner == request.user
    is_race_creator = race.created_by == request.user
    can_manage = is_owner or is_race_creator
    
    # Check if the user is a driver in this race but not in this team
    user_driver = RaceDriver.objects.filter(race=race, user=request.user).first()
    can_join = user_driver and not TeamMembership.objects.filter(
        team=team, driver=user_driver
    ).exists()
    
    context = {
        'team': team,
        'race': race,
        'memberships': memberships,
        'available_drivers': available_drivers,
        'is_owner': is_owner,
        'is_race_creator': is_race_creator,
        'can_manage': can_manage,
        'can_join': can_join,
        'user_driver': user_driver,
    }
    return render(request, 'teams/team_detail.html', context)


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
    team = get_object_or_404(Team, pk=team_id)
    race = team.race
    
    # Check permissions
    if team.owner != request.user and race.created_by != request.user:
        messages.error(request, "You don't have permission to add members to this team.")
        return redirect('teams:detail', pk=team.pk)
    
    if request.method == 'POST':
        driver_id = request.POST.get('driver_id')
        role = request.POST.get('role', 'Driver')
        
        try:
            driver = RaceDriver.objects.get(pk=driver_id, race=race)
            
            # Check if driver is already in this team
            if TeamMembership.objects.filter(team=team, driver=driver).exists():
                messages.warning(request, f"{driver.user.get_full_name()} is already in this team.")
            else:
                TeamMembership.objects.create(
                    team=team,
                    driver=driver,
                    role=role
                )
                messages.success(
                    request, 
                    f"{driver.user.get_full_name()} added to {team.name} as {role}."
                )
        except RaceDriver.DoesNotExist:
            messages.error(request, "Invalid driver selected.")
        
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
    team = get_object_or_404(Team, pk=team_id)
    race = team.race
    
    # Get the user's driver record for this race
    user_driver = get_object_or_404(RaceDriver, race=race, user=request.user)
    
    # Check if already in the team
    if TeamMembership.objects.filter(team=team, driver=user_driver).exists():
        messages.info(request, f"You're already a member of {team.name}.")
        return redirect('teams:detail', pk=team.pk)
    
    if request.method == 'POST':
        # Add the user to the team
        TeamMembership.objects.create(
            team=team,
            driver=user_driver,
            role='Driver'  # Default role
        )
        messages.success(request, f"You've joined {team.name}!")
        return redirect('teams:detail', pk=team.pk)
    
    return redirect('teams:detail', pk=team.pk)