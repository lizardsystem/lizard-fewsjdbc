"""Datetime utils"""

from django.conf import settings
from pytz import timezone


def astimezone(timeseries, tz=timezone(settings.TIME_ZONE)):
    """Localize an "aware" (i.e. non-naive) timeseries."""
    for row in timeseries:
        row['time'] = row['time'].astimezone(tz)
    return timeseries
