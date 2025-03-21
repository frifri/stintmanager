from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Race, RaceDriver, DrivingAssignment
from .forms import RaceForm
from django.contrib import messages
from teams.models import TeamMembership, Team

@login_required
def race_list(request):
    """View to display list of races."""
    races = Race.objects.select_related('created_by').order_by('-start_time')
    
    # Get races where the user is a driver
    participating_races = Race.objects.filter(
        drivers__user=request.user
    ).distinct()
    
    # Get races created by the user
    created_races = races.filter(created_by=request.user)
    
    # Other available races (excluding those where user is already involved)
    other_races = races.exclude(
        id__in=participating_races.values_list('id', flat=True)
    ).exclude(
        id__in=created_races.values_list('id', flat=True)
    )
    
    context = {
        'participating_races': participating_races,
        'created_races': created_races,
        'other_races': other_races,
    }
    return render(request, 'races/race_list.html', context)


@login_required
def race_create(request):
    if request.method == 'POST':
        form = RaceForm(request.POST)
        if form.is_valid():
            race = form.save(commit=False)
            race.created_by = request.user
            race.save()
            messages.success(request, 'Race created successfully!')
            return redirect('races:list')
    else:
        form = RaceForm()
    
    return render(request, 'races/race_form.html', {'form': form, 'title': 'Create Race'})


@login_required
def race_detail(request, pk):
    """View detailed information about a specific race."""
    race = get_object_or_404(Race, pk=pk)
    
    # Check if user is a driver in this race
    user_driver = RaceDriver.objects.filter(race=race, user=request.user).first()
    
    # Check if race has a team
    team = None
    has_team = False
    try:
        # Change this line to get teams using the correct related_name
        teams = race.teams.all()  # Assuming related_name='teams' in the model
        if teams.exists():
            team = teams.first()
            has_team = True
    except AttributeError:
        # Handle the case where the relationship doesn't exist yet
        team = None
        has_team = False
    
    # Get team members if team exists
    team_members = TeamMembership.objects.filter(team=team).select_related('user') if team else []
    
    # Get all drivers for this race - this was missing
    drivers = RaceDriver.objects.filter(race=race).select_related('user')
    
    # Get all driving assignments for this race
    assignments = DrivingAssignment.objects.filter(
        race_driver__race=race
    ).select_related('race_driver', 'race_driver__user').order_by('start_time')
    
    # Check if user is the creator of the race
    is_creator = race.created_by == request.user
    
    # Check if user is already a team member
    is_team_member = user_driver and team and TeamMembership.objects.filter(
        team=team, user=request.user
    ).exists()
    
    context = {
        'race': race,
        'user_driver': user_driver,
        'drivers': drivers,
        'assignments': assignments,
        'is_creator': is_creator,
        'can_join': user_driver and not is_team_member,
        'team': team,
        'has_team': has_team,
        'team_members': team_members,
        'is_team_member': is_team_member,
    }
    return render(request, 'races/race_detail.html', context)


@login_required
def race_edit(request, pk):
    """View to edit an existing race."""
    race = get_object_or_404(Race, pk=pk)
    
    # Check if user is allowed to edit this race
    if race.created_by != request.user:
        messages.error(request, "You don't have permission to edit this race.")
        return redirect('races:detail', pk=race.pk)
    
    if request.method == 'POST':
        form = RaceForm(request.POST, instance=race)
        if form.is_valid():
            form.save()
            messages.success(request, 'Race updated successfully!')
            return redirect('races:detail', pk=race.pk)
    else:
        form = RaceForm(instance=race)
    
    return render(request, 'races/race_form.html', {
        'form': form, 
        'title': 'Edit Race',
        'is_edit': True,
        'race': race
    })


@login_required
def race_delete(request, pk):
    """View to delete an existing race."""
    race = get_object_or_404(Race, pk=pk)
    
    # Check if user is allowed to delete this race
    if race.created_by != request.user:
        messages.error(request, "You don't have permission to delete this race.")
        return redirect('races:detail', pk=race.pk)
    
    if request.method == 'POST':
        # Store the name for the success message
        race_name = race.name
        race.delete()
        messages.success(request, f'Race "{race_name}" has been deleted.')
        return redirect('races:list')
    
    # If it's a GET request, redirect to detail page (the delete should always be POST)
    return redirect('races:detail', pk=race.pk)