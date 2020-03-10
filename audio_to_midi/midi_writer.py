from midiutil import MIDIFile


class MidiWriter(object):
    """
    An object which takes in a list of midi notes and generates
        a midi file from it.
    """

    def __init__(self, outfile, time_window, bpm):
        """
        MidiWriter object constructor.
        
        outfile is the file to be written to.
        time_window is the time window in ms.
        """

        self.midi_file = MIDIFile(1)
        self.midi_file.addTempo(0, 1, bpm)

        self.outfile = outfile
        self.current_tick = 0

        # Determine the number of ticks per note.
        self.tick_window = int(time_window / 100) + 1

    def reset_time(self):
        self.current_tick = 0

    def add_notes(self, note_list):
        """
        notes is a list of midi notes to add at the current
            time step.
            
        Adds each note in the list to the current time step
            with the volume, track and channel specified.
        """
        for notes in note_list:
            for pitch, val in notes.items():
                if pitch:
                    self.midi_file.addNote(
                        val["track"],
                        val["channel"],
                        pitch,
                        self.current_tick,
                        self.tick_window * val["duration"],
                        val["volume"],
                    )

            self.current_tick += self.tick_window

    def write_file(self):
        """
        Writes the midi data to the output file.
        """

        with open(self.outfile, "wb") as outfile:
            self.midi_file.writeFile(outfile)
