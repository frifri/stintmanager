#!/usr/bin/env python
"""
Script to generate sample data for the StintManager application.
"""
import os
import sys
import django
import random
from datetime import datetime, timedelta

# Set up Django
# Get the project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add the project root to the Python path
sys.path.insert(0, BASE_DIR)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stintmanager.settings')
django.setup()

from django.utils import timezone
from core.models import User
from races.models import Race, RaceDriver, AvailabilityWindow, DrivingAssignment
from teams.models import Team, TeamMembership


def create_users():
    """Create sample users."""
    print("Creating sample users...")
    
    users = [
        {
            'email': 'john.doe@example.com',
            'password': 'password123',
            'first_name': 'John',
            'last_name': 'Doe',
            'is_staff': False,
        },
        {
            'email': 'jane.smith@example.com',
            'password': 'password123',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'is_staff': False,
        },
        {
            'email': 'bob.johnson@example.com',
            'password': 'password123',
            'first_name': 'Bob',
            'last_name': 'Johnson',
            'is_staff': False,
        },
        {
            'email': 'alice.williams@example.com',
            'password': 'password123',
            'first_name': 'Alice',
            'last_name': 'Williams',
            'is_staff': False,
        },
        {
            'email': 'charlie.brown@example.com',
            'password': 'password123',
            'first_name': 'Charlie',
            'last_name': 'Brown',
            'is_staff': False,
        },
    ]
    
    created_users = []
    for user_data in users:
        is_staff = user_data.pop('is_staff')
        try:
            user = User.objects.create_user(**user_data)
            user.is_staff = is_staff
            user.save()
            created_users.append(user)
            print(f"  Created user: {user.email}")
        except django.db.utils.IntegrityError:
            # User already exists
            user = User.objects.get(email=user_data['email'])
            created_users.append(user)
            print(f"  User already exists: {user.email}")
    
    return created_users


def create_races(users):
    """Create sample races."""
    print("Creating sample races...")
    
    # Get admin user for race creation
    admin = User.objects.filter(is_superuser=True).first()
    if not admin:
        admin = users[0]  # Fallback to first user if no admin
    
    races = [
        {
            'name': '24 Hours of Le Mans 2025',
            'description': 'The 93rd running of the 24 Hours of Le Mans, the world\'s oldest active sports car race in endurance racing.',
            'start_time': timezone.now() + timedelta(days=30),
            'duration_hours': 24,
            'track_name': 'Circuit de la Sarthe',
            'avg_lap_time_seconds': 220,
            'created_by': admin,
        },
        {
            'name': '12 Hours of Sebring 2025',
            'description': 'The 74th Annual Mobil 1 Twelve Hours of Sebring, one of the oldest continuously running auto races in the U.S.',
            'start_time': timezone.now() + timedelta(days=60),
            'duration_hours': 12,
            'track_name': 'Sebring International Raceway',
            'avg_lap_time_seconds': 110,
            'created_by': admin,
        },
        {
            'name': '6 Hours of Spa-Francorchamps 2025',
            'description': 'The 6 Hours of Spa-Francorchamps is an endurance race for sports cars held at Circuit de Spa-Francorchamps in Belgium.',
            'start_time': timezone.now() + timedelta(days=90),
            'duration_hours': 6,
            'track_name': 'Circuit de Spa-Francorchamps',
            'avg_lap_time_seconds': 135,
            'created_by': admin,
        },
    ]
    
    created_races = []
    for race_data in races:
        race, created = Race.objects.get_or_create(
            name=race_data['name'],
            defaults=race_data
        )
        created_races.append(race)
        action = "Created" if created else "Found existing"
        print(f"  {action} race: {race.name}")
    
    return created_races


def assign_drivers_to_races(users, races):
    """Assign drivers to races."""
    print("Assigning drivers to races...")
    
    # Available timezones for variety
    timezones = ['America/New_York', 'Europe/London', 'Europe/Paris', 
                 'Asia/Tokyo', 'Australia/Sydney', 'America/Los_Angeles']
    
    created_drivers = []
    
    # For each race, assign 2-4 random drivers
    for race in races:
        # Select random number of drivers for this race
        num_drivers = random.randint(2, min(4, len(users)))
        selected_users = random.sample(users, num_drivers)
        
        for user in selected_users:
            timezone_name = random.choice(timezones)
            driver, created = RaceDriver.objects.get_or_create(
                race=race,
                user=user,
                defaults={
                    'timezone': timezone_name
                }
            )
            created_drivers.append(driver)
            action = "Created" if created else "Found existing"
            print(f"  {action} driver: {user.get_full_name()} for race: {race.name}")
            
            # Add availability windows for this driver
            create_availability_windows(driver, race)
    
    return created_drivers


def create_availability_windows(driver, race):
    """Create random availability windows for a driver in a race."""
    # Delete existing windows for this driver
    AvailabilityWindow.objects.filter(race_driver=driver).delete()
    
    # Number of windows to create
    num_windows = random.randint(1, 3)
    
    for _ in range(num_windows):
        # Random start time within the race duration
        hours_offset = random.randint(0, race.duration_hours - 2)
        window_start = race.start_time + timedelta(hours=hours_offset)
        
        # Random duration between 2 and 6 hours
        window_duration = random.randint(2, min(6, race.duration_hours - hours_offset))
        window_end = window_start + timedelta(hours=window_duration)
        
        window = AvailabilityWindow.objects.create(
            race_driver=driver,
            start_time=window_start,
            end_time=window_end
        )
        print(f"    Created availability window for {driver.user.get_full_name()}: {window_start.strftime('%Y-%m-%d %H:%M')} - {window_end.strftime('%Y-%m-%d %H:%M')}")


def create_teams(users, races):
    """Create teams for races."""
    print("Creating teams...")
    
    created_teams = []
    
    # Create one team per race
    for race in races:
        # Team owner is the race creator
        owner = race.created_by
        
        team_name = f"Team {race.track_name.split()[0]}"
        team, created = Team.objects.get_or_create(
            name=team_name,
            defaults={
                'race': race,
                'owner': owner,
                'description': f"Official team for the {race.name} race."
            }
        )
        created_teams.append(team)
        action = "Created" if created else "Found existing"
        print(f"  {action} team: {team.name} for race: {race.name}")
        
        # Add race drivers as team members
        drivers = RaceDriver.objects.filter(race=race)
        for driver in drivers:
            membership, m_created = TeamMembership.objects.get_or_create(
                team=team,
                user=driver.user,
                defaults={
                    'role': 'Driver' if driver.user != owner else 'Team Manager'
                }
            )
            action = "Added" if m_created else "Found existing"
            print(f"    {action} team member: {driver.user.get_full_name()} as {membership.role}")
    
    return created_teams


def create_driving_assignments(races):
    """Create driving assignments for races."""
    print("Creating driving assignments...")
    
    # Clear existing assignments
    DrivingAssignment.objects.all().delete()
    
    for race in races:
        print(f"  Creating assignments for race: {race.name}")
        
        # Get all drivers for this race
        drivers = list(RaceDriver.objects.filter(race=race))
        if not drivers:
            print(f"    No drivers for race: {race.name}")
            continue
        
        # Calculate stint duration based on race length
        if race.duration_hours <= 6:
            stint_duration = 2  # 2-hour stints for shorter races
        else:
            stint_duration = 3  # 3-hour stints for longer races
        
        # Create assignments for the full race duration
        current_time = race.start_time
        end_time = race.start_time + timedelta(hours=race.duration_hours)
        
        while current_time < end_time:
            # Pick a random driver for this stint
            driver = random.choice(drivers)
            
            # Calculate stint end time (capped by race end)
            stint_end = min(current_time + timedelta(hours=stint_duration), end_time)
            
            # Check if driver has availability for this stint
            has_availability = AvailabilityWindow.objects.filter(
                race_driver=driver,
                start_time__lte=current_time,
                end_time__gte=stint_end
            ).exists()
            
            # If no availability, try another driver
            if not has_availability:
                # Try all drivers
                found_driver = False
                for alt_driver in drivers:
                    has_availability = AvailabilityWindow.objects.filter(
                        race_driver=alt_driver,
                        start_time__lte=current_time,
                        end_time__gte=stint_end
                    ).exists()
                    if has_availability:
                        driver = alt_driver
                        found_driver = True
                        break
                
                # If no driver has availability for this slot, create one
                if not found_driver:
                    window = AvailabilityWindow.objects.create(
                        race_driver=driver,
                        start_time=current_time,
                        end_time=stint_end
                    )
                    print(f"    Created additional availability window for {driver.user.get_full_name()}")
            
            # Create the driving assignment
            assignment = DrivingAssignment.objects.create(
                race_driver=driver,
                start_time=current_time,
                end_time=stint_end,
                notes=f"Stint {int((current_time - race.start_time).total_seconds() / 3600) + 1}"
            )
            
            print(f"    Created assignment for {driver.user.get_full_name()}: {current_time.strftime('%Y-%m-%d %H:%M')} - {stint_end.strftime('%Y-%m-%d %H:%M')}")
            
            # Move to next stint
            current_time = stint_end


def main():
    """Main function to create sample data."""
    print("=== Creating Sample Data ===")
    
    # Create users
    users = create_users()
    
    # Create races
    races = create_races(users)
    
    # Assign drivers to races
    drivers = assign_drivers_to_races(users, races)
    
    # Create teams
    teams = create_teams(users, races)
    
    # Create driving assignments
    create_driving_assignments(races)
    
    print("\n=== Sample data creation complete! ===")
    print("Users created:")
    for user in users:
        print(f"  - {user.email} (password: password123)")
    
    print("\nRaces created:")
    for race in races:
        print(f"  - {race.name} at {race.track_name}")
    
    print("\nNavigate to http://127.0.0.1:8000/ and log in with one of the sample users or the admin user.")


if __name__ == "__main__":
    main()