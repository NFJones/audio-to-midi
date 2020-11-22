import logging

from midiutil import MIDIFile


class MidiWriter(object):
    """
    An object which takes in a list of midi notes and generates
        a midi file from it.
    """

    def __init__(self, outfile):
        """
        MidiWriter object constructor.

        outfile is the file to be written to.
        """

        self.midi_file = MIDIFile(numTracks=1, eventtime_is_ticks=True)

        self.outfile = outfile
        self.current_beat = 0
        self.ticks_per_beat = 8

        self.note_state = {}

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.write_file()

    def add_notes(self, note_list):
        """
        notes is a list of midi notes to add at the current
            time step.

        Adds each note in the list to the current time step
            with the volume, track and channel specified.
        """
        for notes in note_list:
            for pitch, val in notes.items():
                self.midi_file.addNote(
                    val["track"],
                    val["channel"],
                    pitch,
                    self.current_beat * self.ticks_per_beat,
                    val["duration"] * self.ticks_per_beat,
                    val["volume"],
                )

    def next_beat(self):
        self.current_beat += 1

    def write_file(self):
        """
        Writes the midi data to the output file.
        """

        with open(self.outfile, "wb") as outfile:
            self.midi_file.writeFile(outfile)
