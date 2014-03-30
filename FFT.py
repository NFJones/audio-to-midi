import cmath
import numpy as np
import math

from notes import notes
import MidiWriter

class FFT(object):
    """
    An object which takes in a list of audio samples and transforms
        them into midi data which is written out to a .mid file.
    """
    
    def __init__(self, samples, rate, time_quantum, activation_level, condense, single_note, outfile, progress_bar, app):
        """
        FFT object constructor.
        
        samples is a list of raw audio samples.
        rate is the sampling frequency of the audio samples.
        time_quantum is the interval (in ms) over which to compute the fft's.
        activation_level is the volume cutoff percentage for frequencies.
        outfile is the MIDI file to be written to.
        """
        
        self.samples = samples
        self.length = len(samples)
        self.rate = rate
        self.time_quantum = time_quantum
        self.activation_level = activation_level
        self.condense = condense
        self.single_note = single_note
        self.progress_bar = progress_bar
        self.app = app
        
        #Get the number of samples per time_quantum
        self.step_size = self.time_quantum_to_step_size(self.time_quantum, self.rate)
        self.outfile = outfile
        
    def get_samples(self):
        """
        Accessor for audio samples.
        """
        
        return self.samples
        
    def get_length(self):
        """
        Accessor for audio samples length.
        """
        
        return self.length
        
    def get_amplitudes(self):
        """
        Accessor for fft amplitudes.
        """
        
        return self.amplitudes
        
    def get_rate(self):
        """
        Accessor for audio sample rate.
        """
        
        return self.rate
        
    def get_time_quantum(self):
        """
        Accessor for time quantum.
        """
        
        return self.time_quantum
        
    def get_activation_level(self):
        """
        Accessor for volume cutoff.
        """
        
        return self.activation_level
        
    def get_step_size(self):
        """
        Accessor for sample step size.
        """
        
        return self.step_size
        
    def get_outfile(self):
        """
        Accessor for output file string.
        """
        
        return self.outfile
        
    def time_quantum_to_step_size(self, time_quantum, rate):
        """
        time_quantum is the time in ms over which to compute fft's.
        rate is the audio sampling rate in samples/sec.
        
        Transforms the time quantum into an index step size and 
            returns the result.
        """
        
        # rate/1000(samples/ms) * time_quantum(ms) = step_size(samples)
        rate_per_ms = rate/1000
        step_size = rate_per_ms * time_quantum
        
        return step_size
        
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
            for key, val in notes.items():
                key = key - 7
                #Find the freq's equivalence class, adding the amplitudes.
                if val[0] <= freq[0] <= val[2]:
                    if key in reduced_freqs.keys():
                        prev = reduced_freqs[key]
                        prev += freq[1]
                        reduced_freqs.update({key: prev})
                        
                    else:
                        reduced_freqs.update({key: freq[1]})
            
        return reduced_freqs
        
    def freqs_to_midi(self, freq_list):
        """
        freq_list is a list of frequencies with normalized amplitudes.
        
        Takes a list of notes and transforms the amplitude to a
            midi volume as well as adding track and channel info.
        """
        
        activation_level = self.get_activation_level()/100.0
        midi_list = []
        for freqs in freq_list:
            midi_notes = {}
            for key, val in freqs.items():
                if val >= activation_level:
                    #The key is the midi note.
                    midi_notes.update({key: {'track': 0, 'channel': 1, 'volume': int(127*val), 'duration': 1}})
            if self.single_note:
                max_note = None
                index = None
                for note, info in midi_notes.items():
                    if max_note == None:
                        max_note = midi_notes[note]
                    elif info['volume'] > max_note['volume']:
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
        #Determine the true amplitudes
        for i in range(size/2):
            re = amplitudes[i].real
            im = amplitudes[i].imag
            amplitude = math.sqrt(re*re+im*im)
            
            #Determine the frequency in Hz
            freq = i * float(self.get_rate()) / size
            if freq > 20000.0:
                break
            else:
                freqs.append([freq, amplitude])
        
        #Transform the frequency info into midi compatible data.
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
                            if next_midi[note]['volume'] > cur_midi[note]['volume']:
                                new_volume = next_midi[note]['volume']
                                
                            else:
                                new_volume = cur_midi[note]['volume']
                            info.update({'duration': info['duration'] + 1, 'volume': new_volume})
                            cur_midi.update({note: info})
                            next_midi.pop(note, None)
                            
                        else:
                            break
                            
                        j += 1
                        
        return midi_list
        
    def calculate(self):
        """
        Performs the fft for each time step and uses fft_to_frequencies
            to transform the result into midi compatible data. This data
            is then passed to a midi file writer to be written out.
        """
        
        samples = self.get_samples()
        steps = len(samples) / self.get_step_size()
        increment = 80.0/steps
        total = 10.0
        step_size = self.get_step_size()
        midi_writer = MidiWriter.MidiWriter(self.get_outfile(), self.get_time_quantum())
        freqs = []
        
        for i in range(steps):
            if i < steps - 1:
                amplitudes = np.fft.fft(samples[step_size*i:(step_size*i+step_size)])
                
            else:
                amplitudes = np.fft.fft(samples[step_size*i:])
                
            freqs.append(self.fft_to_frequencies(amplitudes))
            new_value = int(total + increment)
            total += increment
            self.progress_bar.setValue(new_value)
            self.app.processEvents()
            
        freqs = self.normalize_freqs(freqs)
        if self.condense:
            midi_list = self.condense_midi_notes(self.freqs_to_midi(freqs))
        else:
            midi_list = self.freqs_to_midi(freqs)
        self.progress_bar.setValue(93)
        self.app.processEvents()
        midi_writer.add_notes(midi_list)
        self.progress_bar.setValue(97)
        self.app.processEvents()
        midi_writer.write_file()
        self.progress_bar.setValue(100)
        self.app.processEvents()

        