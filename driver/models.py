from django.db import models

from common.models import StintManagerModel


class Driver(StintManagerModel):
    """ "Driver model. This is not necessarily associated to a User"""

    name = models.CharField(max_length=255)
