import re

# Global variables
BASE_FREQUENCIES = {'C':16.35,
                    'C#':17.32, 
                    'D':18.35,
                    'D#':19.45,
                    'E':20.60,
                    'F':21.83,
                    'F#':23.12,
                    'G':24.50,
                    'G#':25.96,
                    'A':27.50,
                    'A#':29.14,
                    'B':30.87}

MIN_FREQ, MIN_FREQ_NAME = sorted([(value, key) for key, value in BASE_FREQUENCIES.items()])[0]
MAX_FREQ, MAX_FREQ_NAME = sorted([(value, key) for key, value in BASE_FREQUENCIES.items()])[-1]

def get_frequency(note, octave):
    """Returns the frequency associated to a `note` played at a given `octave`."""
    return BASE_FREQUENCIES[note]*2**octave

def get_note(freq, split=True):
    """If `split` is True:
       Returns a tuple (`base_note`, `octave`) corresponding to the closest note to frequency
       `freq`.
       `base_note` belongs to regexp [A-G]#?
       Else:
       Returns a string representation of the closest note with `base_note` and `octave`
       concatenated."""
    base_note, octave = get_closest_note(freq)
    if split:
        return (base_note, octave)
    else:
        return "%s%d" % (base_note, octave)

def get_base_frequency_and_power_of_two(freq):
    i = 0
    while freq >= 2*MIN_FREQ:
        freq /= 2.
        i += 1
    return freq, i

def get_closest_note(freq):
    freq, i = get_base_frequency_and_power_of_two(freq)
    if abs(freq - 2*MIN_FREQ) < abs(freq - MAX_FREQ):
        return MIN_FREQ_NAME, i+1
    return min([(abs(freq - fref), ref_note)
                for ref_note, fref in BASE_FREQUENCIES.items()])[1], i

def split_note_name(note):
    match = re.match('([A-G]#?)(\d+)$', note)
    return match.group(1), int(match.group(2))
