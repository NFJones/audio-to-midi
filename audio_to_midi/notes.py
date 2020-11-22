def generate():
    """
    Generates a dict of midi note codes with their corresponding
        frequency ranges.
    """

    # C0
    base = [31.785450996, 32.703195662, 33.675512266]
    # 12th root of 2
    multiplier = 1.05946309436

    notes = {0: base}
    for i in range(1, 128):
        mid = multiplier * notes[i - 1][1]
        low = (mid + notes[i - 1][1]) / 2.0
        high = (mid + (multiplier * mid)) / 2.0
        notes.update({i: [low, mid, high]})

    return notes
