from midiutil import MIDIFile


class MidiWriter(object):
    """
    An object which takes in a list of midi notes and generates
        a midi file from it.
    """

    def __init__(self, outfile, time_quantum):
        """
        MidiWriter object constructor.
        
        outfile is the file to be written to.
        time_quantum is the time window in ms.
        """

        self.pattern = MIDIFile(1)
        self.outfile = outfile
        self.current_tick = 0

        # Determine the number of ticks per note.
        self.tick_quantum = int(time_quantum / 100) + 1

    def reset_time(self):
        self.current_tick = 0

    def add_notes(self, note_list, channel):
        """
        notes is a list of midi notes to add at the current
            time step.
            
        Adds each note in the list to the current time step
            with the volume, track and channel specified.
        """
        for notes in note_list:
            for pitch, val in notes.items():
                if pitch >= 0:
                    self.pattern.addNote(
                        val["track"],
                        channel,
                        pitch,
                        self.current_tick,
                        self.tick_quantum * val["duration"],
                        val["volume"],
                    )

            self.current_tick += self.tick_quantum

    def write_file(self):
        """
        Writes the midi pattern to the output file.
        """

        with open(self.outfile, "wb") as outfile:
            self.pattern.writeFile(outfile)
