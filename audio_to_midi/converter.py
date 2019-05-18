import cmath
import numpy
import math

from audio_to_midi import midi_writer, notes


class Converter(object):
    """
    An object which takes in a list of audio samples and transforms
        them into midi data which is written out to a .mid file.
    """

    def __init__(
        self,
        samples=None,
        samplerate=None,
        channels=0,
        time_quantum=None,
        activation_level=None,
        condense=None,
        single_note=None,
        outfile=None,
        progress_callback=None,
    ):
        """
        FFT object constructor.
        
        samples is a list of raw audio samples.
        rate is the sampling frequency of the audio samples.
        time_quantum is the interval (in ms) over which to compute the fft's.
        activation_level is the volume cutoff percentage for frequencies.
        outfile is the MIDI file to be written to.
        """

        self.samples = samples
        self.channels = channels
        self.length = len(samples)
        self.samplerate = samplerate
        self.time_quantum = time_quantum
        self.activation_level = activation_level
        self.condense = condense
        self.single_note = single_note
        self.outfile = outfile
        self.progress_callback = progress_callback
        self.notes = notes.generate()
        self.bpm = int((60 * 1000) / self.time_quantum)

        # Get the number of samples per time_quantum
        self.step_size = self.time_quantum_to_step_size(
            self.time_quantum, self.samplerate
        )

    def time_quantum_to_step_size(self, time_quantum, rate):
        """
        time_quantum is the time in ms over which to compute fft's.
        rate is the audio sampling rate in samples/sec.
        
        Transforms the time quantum into an index step size and 
            returns the result.
        """

        # rate/1000(samples/ms) * time_quantum(ms) = step_size(samples)
        rate_per_ms = rate / 1000
        step_size = rate_per_ms * time_quantum

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
                key = key - 7
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

        activation_level = self.activation_level / 100.0
        midi_list = []
        for freqs in freq_list:
            midi_notes = {}
            for key, val in freqs.items():
                if val >= activation_level:
                    # The key is the midi note.
                    midi_notes.update(
                        {
                            key: {
                                "track": 0,
                                "channel": channel,
                                "volume": int(127 * val),
                                "duration": 1,
                            }
                        }
                    )
            if self.single_note:
                max_note = None
                index = None
                for note, info in midi_notes.items():
                    if max_note == None:
                        max_note = midi_notes[note]
                    elif info["volume"] > max_note["volume"]:
                        max_note = midi_notes[note]
                        index = note
                if max_note == None:
                    midi_notes = {}
                else:
                    midi_notes = {index: max_note}
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
            freq = i * float(self.samplerate) / size
            if freq > 20000.0:
                break
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
            for key, freq in freqs.items():
                if freq > max_amplitude:
                    max_amplitude = freq

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

    def convert(self):
        """
        Performs the fft for each time step and uses fft_to_frequencies
            to transform the result into midi compatible data. This data
            is then passed to a midi file writer to be written out.
        """

        steps = int(len(self.samples) / self.step_size)
        writer = midi_writer.MidiWriter(self.outfile, self.time_quantum, self.bpm)
        freqs = []

        samples = []
        for i in range(self.channels):
            samples.append([s[i] for s in self.samples])
        self.samples = samples

        current = 0
        total = self.channels * steps
        for channel in range(self.channels):
            freqs = []
            writer.reset_time()

            for i in range(steps):
                current += 1
                if self.progress_callback:
                    self.progress_callback(current, total)

                if i < steps - 1:
                    amplitudes = numpy.fft.fft(
                        self.samples[channel][
                            self.step_size * i : (self.step_size * i + self.step_size)
                        ]
                    )

                else:
                    amplitudes = numpy.fft.fft(
                        self.samples[channel][self.step_size * i :]
                    )

                freqs.append(self.fft_to_frequencies(amplitudes))

            freqs = self.normalize_freqs(freqs)
            if self.condense:
                midi_list = self.condense_midi_notes(self.freqs_to_midi(freqs, channel))
            else:
                midi_list = self.freqs_to_midi(freqs, channel)

            writer.add_notes(midi_list)

        writer.write_file()
