from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.functions import Lower

from common.models import StintManagerModel
from common.types import GameChoices


class Team(StintManagerModel):
    """Represent the Team object"""

    name = models.CharField(max_length=255)
    games = ArrayField(models.CharField(max_length=255), choices=GameChoices.choices)
    paint_link = models.URLField(blank=True, null=True)

    class Meta:
        constraints = [models.UniqueConstraint(Lower("name"), name="unique_lower_name")]

    def __repr__(self) -> str:
        return f"Team named {self.name}"
