from math import floor


def format_time(timeparts, with_letters=False):
    """
    TODO: Write documentation
    """

    h, m, s = timeparts

    if with_letters:
        return f'{h}h {m}m {s}s'
    else:
        prefix = ''

        if h > 0:
            prefix = f'{str(h).zfill(2)}:'

        return f'{prefix}{str(m).zfill(2)}:{str(s).zfill(2)}'


def get_time_parts(seconds):
    """
    TODO: Write documentation
    """

    m = floor((seconds // 60) % 60)
    h = floor(seconds // 3600)
    s = floor(seconds % 60)

    return (h, m, s)


def get_ideal_size(original, desired):
    """
    TODO: Write documentation
    """

    ratioOrig = original[0] / original[1]
    ratioDes = desired[0] / desired[1]

    if ratioDes > ratioOrig:
        return (floor(original[0] * (desired[1] / original[1])), desired[1])
    else:
        return (desired[0], floor(original[1] * (desired[0] / original[0])))
