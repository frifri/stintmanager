from django.contrib.auth import get_user_model
from django.db import models

from common.models import StintManagerModel
from race.models import Race
from team.models import Team

UserModel = get_user_model()


class RaceCalendar(StintManagerModel):
    """Model representing the calendar for a specific race"""

    race = models.ForeignKey(Race, on_delete=models.DO_NOTHING)
    team = models.ForeignKey(Team, on_delete=models.DO_NOTHING)


class DriverAvailability(StintManagerModel):
    """Model representing driver availability for a race"""

    calendar = models.ForeignKey(RaceCalendar, on_delete=models.CASCADE)
    driver = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
