from __future__ import annotations

from django.db import models

from common.models import StintManagerModel
from common.types import CAR_CHOICES, TRACK_CHOICES, GameChoices


class Race(StintManagerModel):
    """Represent the Race object"""

    name = models.CharField(max_length=255)
    track = models.CharField(max_length=255)
    game = models.CharField(choices=GameChoices.choices, default=GameChoices.IRACING, max_length=255)
    car = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    paint_scheme = models.URLField(blank=True, null=True)
    setup_file = models.FileField(blank=True, null=True)

    def __repr__(self) -> str:
        return f"Race named {self.name} ({self.track} / {self.game})"

    def get_car_choices(self) -> list[tuple[str, str]]:
        """Return the available cars based on the current race game"""
        return CAR_CHOICES[self.game]

    def get_track_choices(self) -> list[tuple[str, str]]:
        """Return the available tracks based on the current race game"""
        return TRACK_CHOICES[self.game]
