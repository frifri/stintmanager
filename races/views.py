from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Race
from .forms import RaceForm
from django.contrib import messages

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