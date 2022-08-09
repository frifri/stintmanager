from django.db import models


class GameChoices(models.TextChoices):
    """Available game choices"""

    IRACING = "iRacing"


BMW_M4_GT3 = "bmw_m4_gt3"
LA_SARTHE = "circuit_de_la_sarthe"

CAR_CHOICES = {
    GameChoices.IRACING: [
        (BMW_M4_GT3, "BMW M4 GT3"),
    ]
}

TRACK_CHOICES = {
    GameChoices.IRACING: [
        (LA_SARTHE, "Circuit de la Sarthe"),
    ]
}
