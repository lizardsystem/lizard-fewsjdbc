"""Datetime utils"""

from django.conf import settings
from pytz import timezone


def astimezone(timeseries, tz=timezone(settings.TIME_ZONE)):
    """Localize an "aware" (i.e. non-naive) timeseries."""
    for row in timeseries:
        row['time'] = row['time'].astimezone(tz)
    return timeseries


def asstring(dt):
    """Custom datetime formatting."""
    fmt = getattr(settings, 'DATETIME_FORMAT_FEWSJDBC', None)
    return dt.strftime(fmt) if fmt else str(dt)
