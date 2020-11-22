import cmath
import numpy
import math
import functools
import soundfile
import logging

from multiprocessing import Pool
from audio_to_midi import midi_writer, notes


class Converter(object):
    """
    An object which takes in a list of audio samples and transforms
        them into midi data which is written out to a .mid file.
    """

    def __init__(
        self,
        infile=None,
        outfile=None,
        time_window=None,
        activation_level=None,
        condense=None,
        note_count=None,
        progress_callback=None,
        threads=1,
    ):
        """
        FFT object constructor.

        samples is a list of raw audio samples.
        rate is the sampling frequency of the audio samples.
        time_window is the interval (in ms) over which to compute the fft's.
        activation_level is the volume cutoff percentage for frequencies.
        outfile is the MIDI file to be written to.
        """

        self.infile = infile
        self.outfile = outfile
        self.threads = threads

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

        # Get the number of samples per time_window
        self.step_size = self.time_window_to_step_size(
            self.time_window, self.info.samplerate
        )

        steps = self.info.frames // self.step_size
        self.total = self.info.channels * steps + 1
        self.current = 0

        self.max_freq = self.info.samplerate / 2
        self.min_freq = 1000 / self.time_window

        logging.info("Window: {} ms".format(self.time_window))
        logging.info("Bins: {}".format(1000 / self.time_window))
        logging.info("Frequencies: min = {} Hz, max = {} Hz".format(self.min_freq, self.max_freq))

    def _increment_progress(self):
        if self.progress_callback:
            self.current += 1
            self.progress_callback(self.current, self.total)

    def time_window_to_step_size(self, time_window, rate):
        """
        time_window is the time in ms over which to compute fft's.
        rate is the audio sampling rate in samples/sec.

        Transforms the time window into an index step size and
            returns the result.
        """

        # rate/1000(samples/ms) * time_window(ms) = step_size(samples)
        rate_per_ms = rate / 1000
        step_size = rate_per_ms * time_window

        return int(step_size)

    def reduce_freqs(self, freqs):
        """
        freqs is a list of amplitudes produced by fft_to_frequencies().

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

    def freqs_to_midi(self, freq_list, channel):
        """
        freq_list is a list of frequencies with normalized amplitudes.

        Takes a list of notes and transforms the amplitude to a
            midi volume as well as adding track and channel info.
        """

        midi_list = []
        max_val = 0.0
        for freqs in freq_list:
            midi_notes = {}
            for key, val in freqs.items():
                if val >= self.activation_level:
                    max_val = max(max_val, val)
                    # The key is the midi note.
                    midi_notes.update(
                        {
                            key: {
                                "track": 0,
                                "channel": channel,
                                "volume": int(255 * (val / 100)),
                                "duration": 1,
                            }
                        }
                    )
            if self.note_count > 0:
                sorted_notes = sorted(
                    midi_notes, key=lambda val: midi_notes[val]["volume"]
                )[::-1]
                max_count = min(len(sorted_notes), self.note_count)
                midi_notes = {key: midi_notes[key] for key in sorted_notes[:max_count]}
            midi_list.append(midi_notes)

        return midi_list

    def fft_to_frequencies(self, amplitudes):
        """
        amplitudes is a list of amplitudes produced by the fft.

        Takes a list of amplitudes and transforms it into a list
            of midi notes by passing the list through reduce_freqs()
            and freqs_to_midi().
        """

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
        return self.reduce_freqs(freqs[1:])

    def normalize_freqs(self, freq_list):
        """
        freq list is a list of dicts containing all of the frequency
            data from the wav file.

        Normalizes the amplitudes of every frequency in every time step.
        """

        max_amplitude = 0.0
        for freqs in freq_list:
            for key, amplitude in freqs.items():
                if amplitude > max_amplitude:
                    max_amplitude = amplitude

        for freqs in freq_list:
            for key, amplitude in freqs.items():
                new_amplitude = amplitude / max_amplitude
                freqs.update({key: new_amplitude})

        return freq_list

    def condense_midi_notes(self, midi_list):
        """
        midi_list is a list of dicts containing midi compatible data.

        Combines consecutive notes accross time steps, using the maximum
            volume seen in the list as the resulting note's volume.
        """

        for i in range(len(midi_list)):
            if i < len(midi_list) - 1:
                cur_midi = midi_list[i]

                for note, info in cur_midi.items():
                    j = i + 1

                    while j < len(midi_list) - 1:
                        next_midi = midi_list[j]

                        if note in next_midi.keys():
                            if next_midi[note]["volume"] > cur_midi[note]["volume"]:
                                new_volume = next_midi[note]["volume"]

                            else:
                                new_volume = cur_midi[note]["volume"]
                            info.update(
                                {"duration": info["duration"] + 1, "volume": new_volume}
                            )
                            cur_midi.update({note: info})
                            next_midi.pop(note, None)

                        else:
                            break

                        j += 1

        return midi_list

    def _samples_to_freqs(self, notes, channel, samples):
        freqs = []

        self._increment_progress()

        amplitudes = numpy.fft.fft(samples)

        freqs.append(self.fft_to_frequencies(amplitudes))

        # freqs = self.normalize_freqs(freqs)
        return freqs

    def _channels_to_notes(self, block, writer):
        if self.info.channels == 1:
            block = [[s] for s in block]

        channels = [[] for _ in block[0]]
        notes = [[] for _ in block[0]]

        for sample in block:
            for channel in range(len(sample)):
                channels[channel].append(sample[channel])

        for channel, samples in enumerate(channels):
            freqs = self._samples_to_freqs(notes, channel, samples)
            notes[channel] = self.freqs_to_midi(freqs, channel)

        return notes

    def convert(self):
        """
        Performs the fft for each time step and uses fft_to_frequencies
            to transform the result into midi compatible data. This data
            is then passed to a midi file writer to be written out.
        """

        logging.info(str(self.info.extra_info))

        with midi_writer.MidiWriter(self.outfile) as writer:
            notes = []
            for block in soundfile.blocks(self.infile, blocksize=self.step_size):
                notes.append(self._channels_to_notes(block=block, writer=writer))

            self.current = 0
            for segment in notes:
                self._increment_progress()
                writer.next_beat()
                for channel in segment:
                    writer.add_notes(channel)
