from django.db import models

from common.models import StintManagerModel
from driver.models import Driver


class Race(StintManagerModel):
    """Race model"""

    name = models.CharField(max_length=1000)


class AverageLapTime(StintManagerModel):
    """An average lap time for a race for a driver"""

    average_lap_time = models.DurationField()
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    race = models.ForeignKey(Race, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["driver", "race"], name="uniquetogether_avg_laptime_driver_race")
        ]


class PitStopType(models.TextChoices):
    """Types of Pitstops"""

    Short = "short"
    Long = "long"


class PitStop(StintManagerModel):
    """The pitstop (long/short) model"""

    type = models.TextField(choices=PitStopType.choices, default=PitStopType.Short.name)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    race = models.ForeignKey(Race, on_delete=models.CASCADE)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["driver", "race"], name="uniquetogether_pitstop_driver_race")]
