#------------------------------------------------------------------------------
# Copyright (c) 2005, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: Enthought, Inc.
# Description: <Enthought util package component>
#
# Changed by ejnens: added decimate_until, fixed decimate recusion causing a stack
# overflow, properly use numpy bool arrays
#------------------------------------------------------------------------------

from collections import deque
import logging

import numpy as np
from numpy import arange, array, sqrt, argmax, zeros, absolute

logger = logging.getLogger(__name__)


def decimate_until(x, y, tolerance, max_values=1200, max_steps=35, step_factor=8.0):
    if len(x) <= max_values:
        # nothing to do
        return x, y
    for step in range(max_steps):
        logger.debug('decimate_until: step %s', step)
        # operate on a copy, so the errors don't accumulate
        x2 = x.copy()
        y2 = y.copy()
        x2, y2 = decimate(x2, y2, tolerance)
        if len(x2) > max_values:
            tolerance *= step_factor
        else:
            break
    return x2, y2


def decimate(datetimes, values):
    """ Returns decimated x and y arrays.

    This is Douglas and Peucker's algorithm rewritten to use Numeric arrays.
    Tolerance is usually determined by determining the size that a single pixel
    represents in the units of x and y.

    Compression ratios for large seismic and well data sets can be significant.

    """
    np_datetimes = array(datetimes)
    np_values = array(values)

    RESOLUTION = 2000.0  # Assumption for resolution in pixels.
    x = arange(len(datetimes))  # In fews, the data is pretty evenly spread.
    tolerance = len(datetimes) / RESOLUTION
    y_data_height = np_values.max() - np_values.min()
    y = np.multiply(np_values, len(datetimes) / y_data_height)

    keep = zeros(len(x), dtype=np.bool)
    segments = deque([(0, len(x) - 1)])
    while segments:
        si, ei = segments.pop()
        keep[si] = True
        keep[ei] = True

        # check if the two data points are adjacent
        if ei < (si + 2):
            continue

        # now find the perpendicular distance to each point
        x0 = x[si+1:ei]
        y0 = y[si+1:ei]

        xei_minux_xsi = x[ei] - x[si]
        yei_minux_ysi = y[ei] - y[si]

        top = absolute(xei_minux_xsi * (y[si] - y0) - (x[si] - x0) * yei_minux_ysi)

        # The algorithm currently does an expensive sqrt operation which is not
        # strictly necessary except that it makes the tolerance correspond to a real
        # world quantity.
        bot = sqrt(xei_minux_xsi*xei_minux_xsi + yei_minux_ysi*yei_minux_ysi)
        dist = top / bot

        # find the point that is furthest from line between points si and ei
        index = argmax(dist)

        if dist[index] > tolerance:
            abs_index = index + (si + 1)
            segments.append((si, abs_index))
            segments.append((abs_index, ei))

    return list(np_datetimes[keep]), list(np_values[keep])
