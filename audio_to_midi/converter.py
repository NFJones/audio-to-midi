import logging

from collections import namedtuple
from functools import lru_cache
from operator import attrgetter

import numpy
import soundfile

from audio_to_midi import midi_writer, notes


class Note:
    __slots__ = ["pitch", "velocity", "count"]

    def __init__(self, pitch, velocity, count=0):
        self.pitch = pitch
        self.velocity = velocity
        self.count = count


class Converter:
    def __init__(
        self,
        infile=None,
        outfile=None,
        time_window=None,
        activation_level=None,
        condense=None,
        condense_max=False,
        transpose=0,
        key=None,
        note_count=None,
        progress=None,
        bpm=60,
    ):

        if infile:
            self.info = soundfile.info(infile)
        else:
            raise RuntimeError("No input provided.")

        self.infile = infile
        self.outfile = outfile
        self.time_window = time_window
        self.condense = condense
        self.condense_max = condense_max
        self.transpose = transpose
        self.key = key
        self.note_count = note_count
        self.progress = progress
        self.bpm = bpm

        self.activation_level = int(127 * activation_level) or 1
        self.block_size = self._time_window_to_block_size(
            self.time_window, self.info.samplerate
        )

        steps = self.info.frames // self.block_size
        self.total = steps
        self.current = 0

        self._determine_ranges()

    def _determine_ranges(self):
        self.notes = notes.generate()
        self.max_freq = min(self.notes[127][-1], self.info.samplerate / 2)
        self.min_freq = max(self.notes[0][-1], 1000 / self.time_window)
        self.bins = self.block_size // 2
        self.frequencies = numpy.fft.fftfreq(self.bins, 1 / self.info.samplerate)[
            : self.bins // 2
        ]

        for i, f in enumerate(self.frequencies):
            if f >= self.min_freq:
                self.min_bin = i
                break
        else:
            self.min_bin = 0
        for i, f in enumerate(self.frequencies):
            if f >= self.max_freq:
                self.max_bin = i
                break
        else:
            self.max_bin = len(self.frequencies)

    def _increment_progress(self):
        if self.progress:
            self.current += 1
            self.progress.update(self.current, self.total)

    @staticmethod
    def _time_window_to_block_size(time_window, rate):
        """
        time_window is the time in ms over which to compute fft's.
        rate is the audio sampling rate in samples/sec.

        Transforms the time window into an index step size and
            returns the result.
        """

        # rate/1000(samples/ms) * time_window(ms) = block_size(samples)
        rate_per_ms = rate / 1000
        block_size = rate_per_ms * time_window

        return int(block_size)

    def _freqs_to_midi(self, freqs):
        """
        freq_list is a list of frequencies with normalized amplitudes.

        Takes a list of notes and transforms the amplitude to a
            midi volume as well as adding track and channel info.
        """

        notes = [None for _ in range(128)]
        for pitch, velocity in freqs:
            if pitch > 127:
                continue
            velocity = min(int(127 * (velocity / 100)), 127)

            if velocity > self.activation_level:
                if not notes[pitch]:
                    notes[pitch] = Note(pitch, velocity)
                else:
                    notes[pitch].velocity = int(
                        ((notes[pitch].velocity * notes[pitch].count) + velocity)
                        / (notes[pitch].count + 1)
                    )
                    notes[pitch].count += 1

        notes = [note for note in notes if note]

        if self.note_count > 0:
            max_count = min(len(notes), self.note_count)
            notes = sorted(notes, key=attrgetter("velocity"))[::-1][:max_count]

        return notes

    def _snap_to_key(self, pitch):
        if self.key:
            mod = pitch % 12
            pitch = (12 * (pitch // 12)) + min(self.key, key=lambda x: abs(x - mod))
        return pitch

    @lru_cache(None)
    def _freq_to_pitch(self, freq):
        for pitch, freq_range in self.notes.items():
            # Find the freq's equivalence class, adding the amplitudes.
            if freq_range[0] <= freq <= freq_range[2]:
                return self._snap_to_key(pitch) + self.transpose
        raise RuntimeError("Unmappable frequency: {}".format(freq[0]))

    def _reduce_freqs(self, freqs):
        """
        freqs is a list of amplitudes produced by _fft_to_frequencies().

        Reduces the list of frequencies to a list of notes and their
            respective volumes by determining what note each frequency
            is closest to. It then reduces the list of amplitudes for each
            note to a single amplitude by summing them together.
        """

        reduced_freqs = []
        for freq in freqs:
            reduced_freqs.append((self._freq_to_pitch(freq[0]), freq[1]))

        return reduced_freqs

    def _samples_to_freqs(self, samples):
        amplitudes = numpy.fft.fft(samples)
        freqs = []

        for index in range(self.min_bin, self.max_bin):
            # frequency, amplitude
            freqs.append(
                [
                    self.frequencies[index],
                    numpy.sqrt(
                        numpy.float_power(amplitudes[index].real, 2)
                        + numpy.float_power(amplitudes[index].imag, 2)
                    ),
                ]
            )

        # Transform the frequency info into midi compatible data.
        return self._reduce_freqs(freqs)

    def _block_to_notes(self, block):
        channels = [[] for _ in range(self.info.channels)]
        notes = [None for _ in range(self.info.channels)]

        for sample in block:
            for channel in range(self.info.channels):
                channels[channel].append(sample[channel])

        for channel, samples in enumerate(channels):
            freqs = self._samples_to_freqs(samples)
            notes[channel] = self._freqs_to_midi(freqs)

        return notes

    def convert(self):
        """
        Performs the fft for each time step and transforms the result
            into midi compatible data. This data is then passed to a
            midi file writer.
        """

        logging.info(str(self.info))
        logging.info("window: {} ms".format(self.time_window))
        logging.info(
            "frequencies: min = {} Hz, max = {} Hz".format(self.min_freq, self.max_freq)
        )

        with midi_writer.MidiWriter(
            outfile=self.outfile,
            channels=self.info.channels,
            time_window=self.time_window,
            bpm=self.bpm,
            condense=self.condense,
            condense_max=self.condense_max,
        ) as writer:
            for block in soundfile.blocks(
                self.infile,
                blocksize=self.block_size,
                always_2d=True,
            ):
                if len(block) == self.block_size:
                    notes = self._block_to_notes(block)
                    writer.add_notes(notes)
                self._increment_progress()
