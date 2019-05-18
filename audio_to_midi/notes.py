import pprint
import math
import sys


def generate():
    """
    Generates a dict of midi note codes with their corresponding
        frequency ranges.
    """

    # C0
    base = [15.892725498, 16.351597831, 16.837756133]
    # 12th root of 2
    multiplier = 1.05946309436

    notes = {0: base}
    for i in range(1, 127):
        mid = multiplier * notes[i - 1][1]
        low = (mid + notes[i - 1][1]) / 2.0
        high = (mid + (multiplier * mid)) / 2.0
        notes.update({i: [low, mid, high]})

    return notes
