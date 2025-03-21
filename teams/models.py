from django.conf import settings
from django.db import models
from core.models import UUIDModel
from races.models import Race, RaceDriver


class Team(UUIDModel):
    name = models.CharField(max_length=100)
    race = models.ForeignKey(
        'races.Race',
        on_delete=models.CASCADE,
        null=True,  # Allow null values
        blank=True,  # Allow blank in forms
        related_name='teams'  # Assuming you want to access teams from race
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_teams'
    )
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.race.name}"

class TeamMembership(UUIDModel):
    team = models.ForeignKey(
        Team, 
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='team_memberships'
    )
    role = models.CharField(
        max_length=50, 
        default='Driver',
        help_text="Role in the team (e.g., 'Driver', 'Team Manager', 'Engineer')"
    )
    
    class Meta:
        unique_together = ['team', 'user']