import cmath
import matplotlib.pyplot as plt
import matplotlib.rcsetup as rcsetup
import numpy as np
import math

from utils.notes import notes
import MidiWriter

class FFT(object):
    def __init__(self, samples, rate, time_quantum, activation_level, outfile):
        self.samples = samples
        self.length = len(samples)
        self.rate = rate
        self.time_quantum = time_quantum
        self.activation_level = activation_level
        self.step_size = self.time_quantum_to_step_size(self.time_quantum, self.rate)
        self.outfile = outfile
        
    def get_samples(self):
        return self.samples
        
    def get_length(self):
        return self.length
        
    def get_amplitudes(self):
        return self.amplitudes
        
    def get_rate(self):
        return self.rate
        
    def get_time_quantum(self):
        return self.time_quantum
        
    def get_activation_level(self):
        return self.activation_level
        
    def get_step_size(self):
        return self.step_size
        
    def get_outfile(self):
        return self.outfile
        
    def show_vars(self):
        print
        print "len(samples): " + str(self.length)
        print "rate: " + str(self.rate)
        print "time_quantum: " + str(self.time_quantum)
        print "step_size: " + str(self.step_size)
        print "steps: " + str(len(self.samples)/self.step_size)
        print "outfile: " + str(self.outfile)
        print
        
    def time_quantum_to_step_size(self, time_quantum, rate):
        rate_per_ms = rate/1000
        step_size = rate_per_ms * time_quantum
        return step_size
        
    def reduce_freqs(self, freqs):
        reduced_freqs = {}
        for freq in freqs:
            for key, val in notes.items():
                if val[0] <= freq[0] <= val[2]:
                    if (key-12) in reduced_freqs.keys():
                        prev = reduced_freqs[key-12]
                        prev.append(freq[1])
                        reduced_freqs.update({key-12: prev})
                    else:
                        reduced_freqs.update({key-12: [freq[1]]})
        for key, val in reduced_freqs.items():
            amplitudes = val
            total = 0.0
            for amplitude in amplitudes:
                total += amplitude
            reduced_freqs.update({key: total})
        max_amplitude = 0.0
        for key, val in reduced_freqs.items():
            if val > max_amplitude:
                max_amplitude = val
        for key, val in reduced_freqs.items():
            new_amplitude = val / max_amplitude
            reduced_freqs.update({key: new_amplitude})
        return reduced_freqs
        
    def freqs_to_midi(self, freqs):
        activation_level = self.get_activation_level()/100.0
        midi_notes = {}
        for key, val in freqs.items():
            if val >= activation_level:
                midi_notes.update({key: {'track': 0, 'channel': 1, 'volume': int(127*val)}})
                
        return midi_notes
        
    def fft_to_frequencies(self, amplitudes):
        size = len(amplitudes)
        freqs = []
        for i in range(size/2):
            re = amplitudes[i].real
            im = amplitudes[i].imag
            amplitude = math.sqrt(re*re+im*im)
            freq = i * float(self.get_rate()) / size
            if freq > 4310.465570470717:
                break
            else:
                freqs.append([freq, amplitude])
        max_freq = 0.0
        for freq in freqs[1:]:
            if freq[1] > max_freq:
                max_freq = freq[1]
        for freq in freqs[1:]:
            freq[1] /= max_freq  
        reduced_freqs = self.reduce_freqs(freqs[1:])
        return self.freqs_to_midi(reduced_freqs)
        
    def calculate(self):
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
            
        
    def plot(self):
        plt.plot(range(self.get_length()), self.get_amplitudes())
        plt.xscale('log', basex=2)
        plt.show()
        