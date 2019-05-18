# audio-to-midi

`audio-to-midi` takes in a sound file and converts it to a multichannel MIDI file. It accomplishes this by performing FFT's on all channels of the audio data at user specified time steps. It then separates the resulting frequency analysis into equivalence classes which correspond to the twelve tone scale; the volume of each class being the average volume of its constituent frequencies. It then formats this data for MIDI and writes it out to a user specified file.
