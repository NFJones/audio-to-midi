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
    
    def __init__(self, samples, rate, time_quantum, activation_level, outfile):
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
            note to a single amplitude by summing them together. The final
            step is to normalize the amplitudes for all of the notes;
            thereby producing a list of notes with a volume percentage
            relative to the maximum note volume.
        """
        
        reduced_freqs = {}
        for freq in freqs:
            for key, val in notes.items():
                key = key - 12
                #Find the freq's equivalence class, adding the amplitudes.
                if val[0] <= freq[0] <= val[2]:
                    if key in reduced_freqs.keys():
                        prev = reduced_freqs[key]
                        prev += freq[1]
                        reduced_freqs.update({key: prev})
                        
                    else:
                        reduced_freqs.update({key: freq[1]})
        
        #Normalize the amplitudes
        max_amplitude = 0.0
        for key, val in reduced_freqs.items():
            if val > max_amplitude:
                max_amplitude = val
        for key, val in reduced_freqs.items():
            new_amplitude = val / max_amplitude
            reduced_freqs.update({key: new_amplitude})
            
        return reduced_freqs
        
    def freqs_to_midi(self, freqs):
        """
        freqs is a list of notes with their normalized volumes.
        
        Takes a list of notes and transforms the amplitude to a
            midi volume as well as adding track and channel info.
        """
        
        activation_level = self.get_activation_level()/100.0
        midi_notes = {}
        for key, val in freqs.items():
            if val >= activation_level:
                #The key is the midi note.
                midi_notes.update({key: {'track': 0, 'channel': 1, 'volume': int(127*val)}})
                
        return midi_notes
        
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
            if freq > 4310.465570470717:
                break
            else:
                freqs.append([freq, amplitude])
        
        #Normalize the amplitudes.
        max_freq = 0.0
        for freq in freqs[1:]:
            if freq[1] > max_freq:
                max_freq = freq[1]
                
        for freq in freqs[1:]:
            freq[1] /= max_freq  
        
        #Transform the frequency info into midi compatible data.
        reduced_freqs = self.reduce_freqs(freqs[1:])
        return self.freqs_to_midi(reduced_freqs)
        
    def calculate(self):
        """
        Performs the fft for each time step and uses fft_to_frequencies
            to transform the result into midi compatible data. This data
            is then passed to a midi file writer to be written out.
        """
        
        samples = self.get_samples()
        steps = len(samples) / self.get_step_size()
        step_size = self.get_step_size()
        midi_writer = MidiWriter.MidiWriter(self.get_outfile(), self.get_time_quantum())
        
        for i in range(steps):
            if i < steps - 1:
                amplitudes = np.fft.fft(samples[step_size*i:(step_size*i+step_size)])
                
            else:
                amplitudes = np.fft.fft(samples[step_size*i:])
                
            midi_notes = self.fft_to_frequencies(amplitudes)
            midi_writer.add_notes(midi_notes)
            
        midi_writer.write_file()
        