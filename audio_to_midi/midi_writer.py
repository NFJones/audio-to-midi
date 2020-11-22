import python3_midi as midi

from collections import defaultdict, namedtuple


class MidiWriter(object):
    def __init__(self, outfile, channels, time_window, bpm=60, condense_notes=False):
        self.outfile = outfile
        self.condense_notes = condense_notes
        self.channels = channels
        self.time_window = time_window
        self.bpm = bpm
        self.note_state = [defaultdict(lambda: False) for _ in range(channels)]

        bps = self.bpm / 60
        self.ms_per_beat = int((1.0 / bps) * 1000)
        self.tick_increment = int(time_window)
        self.skip_count = 1

        self.track = midi.Track(
            events=[
                midi.TimeSignatureEvent(
                    tick=0,
                    numerator=1,
                    denominator=4,
                    metronome=int(self.ms_per_beat / self.time_window),
                    thirtyseconds=32,
                )
            ],
            tick_relative=False,
        )

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self._terminate_notes()
        self.track.append(midi.EndOfTrackEvent(tick=1))

        pattern = midi.Pattern(
            format=1,
            tick_relative=False,
            resolution=self.ms_per_beat,
            tracks=[self.track],
        )

        midi.write_midifile(self.outfile, pattern)

    def _skip(self):
        self.skip_count += 1

    def _reset_skip(self):
        self.skip_count = 1

    @property
    def tick(self):
        ret = 0
        if self._need_increment:
            self._need_increment = False
            ret = self.tick_increment * self.skip_count
            self._reset_skip()
        return ret

    def _note_on(self, channel, pitch, velocity):
        self.note_state[channel][pitch] = True
        self.track.append(
            midi.NoteOnEvent(
                tick=self.tick, channel=channel, pitch=pitch, velocity=velocity
            )
        )

    def _note_off(self, channel, pitch):
        self.note_state[channel][pitch] = False
        self.track.append(
            midi.NoteOffEvent(
                tick=self.tick,
                channel=channel,
                pitch=pitch,
            )
        )

    def add_notes(self, notes):
        """
        notes is a list of midi notes to add at the current
            time step.

        Adds each note in the list to the current time step
            with the volume, track and channel specified.
        """
        self._need_increment = True
        if not self.condense_notes:
            self._terminate_notes()

        for channel, notes in enumerate(notes):
            new_notes = set()
            stale_notes = []
            for note in notes:
                is_active = self.note_state[channel][note.pitch]
                new_notes.add(note.pitch)
                if (not self.condense_notes) or (self.condense_notes and not is_active):
                    self._note_on(channel, note.pitch, note.velocity)

            if self.condense_notes:
                active_notes = [
                    note
                    for note in self.note_state[channel]
                    if self.note_state[channel][note]
                ]
                for note in active_notes:
                    if note not in new_notes:
                        stale_notes.append(note)

                for note in stale_notes:
                    self._note_off(channel, note)

        if self._need_increment:
            self._skip()

    def _terminate_notes(self):
        for channel in range(self.channels):
            for pitch, is_active in self.note_state[channel].items():
                if is_active:
                    self._note_off(channel, pitch)