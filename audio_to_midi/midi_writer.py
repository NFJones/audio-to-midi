from collections import defaultdict

import python3_midi as midi


class NoteState:
    __slots__ = ["is_active", "event_pos", "count"]

    def __init__(self, is_active=False, event_pos=None, count=0):
        self.is_active = is_active
        self.event_pos = event_pos
        self.count = count


class MidiWriter:
    def __init__(
        self, outfile, channels, time_window, bpm=60, condense=False, condense_max=False
    ):
        self.outfile = outfile
        self.condense = condense
        self.condense_max = condense_max
        self.channels = channels
        self.time_window = time_window
        self.bpm = bpm
        self.note_state = [defaultdict(lambda: NoteState()) for _ in range(channels)]

        bps = self.bpm / 60
        self.ms_per_beat = int((1.0 / bps) * 1000)
        self.tick_increment = int(time_window)
        self.skip_count = 1
        self._need_increment = False

    def __enter__(self):
        self.stream = midi.FileStream(self.outfile)
        self.stream.start_pattern(
            format=1,
            tick_relative=False,
            resolution=self.ms_per_beat,
            tracks=[],
        )
        self.stream.start_track(
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
        return self

    def __exit__(self, type, value, traceback):
        self._terminate_notes()
        self.stream.add_event(midi.EndOfTrackEvent(tick=1))
        self.stream.end_track()
        self.stream.end_pattern()
        self.stream.close()

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
        pos = self.stream.add_event(
            midi.NoteOnEvent(
                tick=self.tick, channel=channel, pitch=pitch, velocity=velocity
            )
        )
        self.note_state[channel][pitch] = NoteState(
            True,
            pos,
            1,
        )

    def _note_off(self, channel, pitch):
        self.note_state[channel][pitch] = NoteState()
        self.stream.add_event(
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
        if not self.condense:
            self._terminate_notes()

        for channel, notes in enumerate(notes):
            new_notes = set()
            stale_notes = []
            for note in notes:
                note_state = self.note_state[channel][note.pitch]
                new_notes.add(note.pitch)
                if (not self.condense) or (self.condense and not note_state.is_active):
                    self._note_on(channel, note.pitch, note.velocity)
                elif self.condense and note_state.is_active:
                    event = self.stream.get_event(
                        midi.NoteOnEvent, note_state.event_pos
                    )
                    old_velocity = event.data[1]
                    if self.condense_max:
                        event.data[1] = max(note.velocity, old_velocity)
                    else:
                        count = note_state.count
                        note_state.count += 1
                        event.data[1] = ((old_velocity * count) + note.velocity) // (
                            count + 1
                        )
                    if old_velocity != event.data[1]:
                        self.stream.set_event(event, note_state.event_pos)

            if self.condense:
                active_notes = [
                    note
                    for note in self.note_state[channel]
                    if self.note_state[channel][note].is_active
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
            for pitch, note_state in self.note_state[channel].items():
                if note_state.is_active:
                    self._note_off(channel, pitch)
