import numpy
import math
import soundfile
import logging

from audio_to_midi import midi_writer, notes
from collections import namedtuple
from operator import attrgetter


Note = namedtuple('Note', ['pitch', 'velocity'])


class Converter(object):
    def __init__(
        self,
        infile=None,
        outfile=None,
        time_window=None,
        activation_level=None,
        condense=None,
        note_count=None,
        progress_callback=None,
        bpm=60,
    ):
        self.infile = infile
        self.outfile = outfile

        if self.infile:
            self.info = soundfile.info(self.infile)
        else:
            raise RuntimeError("No input provided.")

        self.notes = notes.generate()

        self.time_window = time_window
        self.activation_level = activation_level
        self.condense = condense
        self.note_count = note_count
        self.progress_callback = progress_callback
        self.bpm = bpm

        # Get the number of samples per time_window
        self.block_size = self._time_window_to_block_size(
            self.time_window, self.info.samplerate
        )

        steps = self.info.frames // self.block_size
        self.total = self.info.channels * steps + 1
        self.current = 0

        self.max_freq = min(20000, self.info.samplerate / 2)
        self.min_freq = max(20.0, 1000 / self.time_window)

    def _increment_progress(self):
        if self.progress_callback:
            self.current += 1
            self.progress_callback(self.current, self.total)

    def _time_window_to_block_size(self, time_window, rate):
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

    def _reduce_freqs(self, freqs):
        """
        freqs is a list of amplitudes produced by _fft_to_frequencies().

        Reduces the list of frequencies to a list of notes and their
            respective volumes by determining what note each frequency
            is closest to. It then reduces the list of amplitudes for each
            note to a single amplitude by summing them together.
        """

        reduced_freqs = {}
        for freq in freqs:
            for key, val in self.notes.items():
                key = key + 12
                # Find the freq's equivalence class, adding the amplitudes.
                if val[0] <= freq[0] <= val[2]:
                    if key in reduced_freqs.keys():
                        prev = reduced_freqs[key]
                        prev += freq[1]
                        reduced_freqs.update({key: prev})

                    else:
                        reduced_freqs.update({key: freq[1]})

        return reduced_freqs

    def _freqs_to_midi(self, freqs, channel):
        """
        freq_list is a list of frequencies with normalized amplitudes.

        Takes a list of notes and transforms the amplitude to a
            midi volume as well as adding track and channel info.
        """

        activation_level = int(127 * self.activation_level) or 1

        max_val = 0.0
        notes = []
        for pitch, val in freqs.items():
            if pitch > 127:
                continue
            velocity = min(int(127 * (val / 100)), 127)

            if velocity > activation_level:
                max_val = max(max_val, val)
                notes.append(Note(pitch, velocity))
        if self.note_count > 0:
            max_count = min(len(notes), self.note_count)
            notes = sorted(notes, key=attrgetter('velocity'))[::-1][:max_count]

        return notes

    def _fft_to_frequencies(self, amplitudes):
        size = len(amplitudes)
        freqs = []
        # Determine the true amplitudes
        for i in range(size // 2):
            re = amplitudes[i].real
            im = amplitudes[i].imag

            amplitude = math.sqrt(re ** 2 + im ** 2)

            # Determine the frequency in Hz
            freq = i * self.info.samplerate / size
            if freq < self.min_freq or freq > self.max_freq:
                # discard junk
                continue
            else:
                freqs.append([freq, amplitude])

        # Transform the frequency info into midi compatible data.
        return self._reduce_freqs(freqs[1:])

    def _samples_to_freqs(self, notes, channel, samples):
        amplitudes = numpy.fft.fft(samples)
        return self._fft_to_frequencies(amplitudes)

    def _block_to_notes(self, block):
        if self.info.channels == 1:
            block = [[s] for s in block]

        channels = [[] for _ in block[0]]
        notes = [[] for _ in block[0]]

        for sample in block:
            for channel in range(len(sample)):
                channels[channel].append(sample[channel])

        for channel, samples in enumerate(channels):
            freqs = self._samples_to_freqs(notes, channel, samples)
            notes[channel] = self._freqs_to_midi(freqs, channel)

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
            condense_notes=self.condense,
        ) as writer:
            for block in soundfile.blocks(self.infile, blocksize=self.block_size):
                notes = self._block_to_notes(block)
                writer.add_notes(notes)
                self._increment_progress()
