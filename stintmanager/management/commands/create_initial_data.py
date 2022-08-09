from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from common import types
from race.models import Race
from race_calendar.models import RaceCalendar
from team.models import Team


class Command(BaseCommand):
    """Creates a set of inital objects to play with"""

    def handle(self, *args, **options):
        now = timezone.now()
        now_and_a_day = now + timedelta(days=1)
        iracing = types.GameChoices.IRACING
        team = Team.objects.create(name="Parabellum Racing team", games=[iracing])

        le_mans = types.TRACK_CHOICES[iracing]
        race = Race.objects.create(
            name="24hrs of le Mans",
            track=le_mans,
            game=iracing,
            car=types.BMW_M4_GT3,
            start_time=now,
            end_time=now_and_a_day,
        )
        RaceCalendar.objects.create(race=race, team=team)
