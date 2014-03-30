import pprint
import math
import sys

def gen_notes():
    """
    Generates a dict of midi note codes with their corresponding
        frequency ranges.
    """
    
    #A0
    base = [26.728271799, 27.5, 28.317617547]
    #12th root of 2
    multiplier = 1.05946309436
    
    notes = {21 : base}
    for i in range(22, 109):
        mid = multiplier * notes[i - 1][1]
        low = (mid + notes[i - 1][1]) / 2.0
        high = (mid + (multiplier * mid)) / 2.0
        notes.update({i : [low, mid, high]})
        
    sys.stdout.write("notes = ")
    pp = pprint.PrettyPrinter()
    pp.pprint(notes)
    
if __name__ == '__main__':
    gen_notes()