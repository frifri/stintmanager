from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from core.models import UUIDModel


class Race(UUIDModel):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    duration_hours = models.PositiveIntegerField()
    track_name = models.CharField(max_length=200)
    avg_lap_time_seconds = models.PositiveIntegerField(
        help_text="Average lap time in seconds"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_races'
    )

    def end_time(self):
        return self.start_time + timezone.timedelta(hours=self.duration_hours)

    def clean(self):
        if self.start_time is not None and self.start_time < timezone.now():
            raise ValidationError("Race cannot start in the past")

    def __str__(self):
        return f"{self.name} at {self.track_name}"


class RaceDriver(UUIDModel):
    race = models.ForeignKey(
        Race,
        on_delete=models.CASCADE,
        related_name='drivers'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='race_participations'
    )
    timezone = models.CharField(
        max_length=50,
        help_text="Driver's timezone (e.g., 'America/New_York')"
    )

    class Meta:
        unique_together = ['race', 'user']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.race.name}"


class AvailabilityWindow(UUIDModel):
    race_driver = models.ForeignKey(
        RaceDriver,
        on_delete=models.CASCADE,
        related_name='availability_windows'
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time")
        
        if (self.start_time < self.race_driver.race.start_time or
            self.end_time > self.race_driver.race.end_time()):
            raise ValidationError("Availability window must be within race time")

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return (f"{self.race_driver.user.get_full_name()} - "
                f"{self.start_time.strftime('%Y-%m-%d %H:%M')} to "
                f"{self.end_time.strftime('%Y-%m-%d %H:%M')}")


class DrivingAssignment(UUIDModel):
    race_driver = models.ForeignKey(
        RaceDriver,
        on_delete=models.CASCADE,
        related_name='driving_assignments'
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    notes = models.TextField(blank=True)

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time")
        
        if (self.start_time < self.race_driver.race.start_time or
            self.end_time > self.race_driver.race.end_time()):
            raise ValidationError("Assignment must be within race time")
        
        if not self.race_driver.availability_windows.filter(
            start_time__lte=self.start_time,
            end_time__gte=self.end_time
        ).exists():
            raise ValidationError("Assignment must be within driver's availability window")

    class Meta:
        ordering = ['start_time']

    def duration_hours(self):
        duration = self.end_time - self.start_time
        return duration.total_seconds() / 3600

    def __str__(self):
        return (f"{self.race_driver.user.get_full_name()} - "
                f"{self.start_time.strftime('%Y-%m-%d %H:%M')} to "
                f"{self.end_time.strftime('%Y-%m-%d %H:%M')}")