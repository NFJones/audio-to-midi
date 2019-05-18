# audio-to-midi

`audio-to-midi` takes in a sound file and converts it to a multichannel MIDI file. It accomplishes this by performing FFT's on all channels of the audio data at user specified time steps. It then separates the resulting frequency analysis into equivalence classes which correspond to the twelve tone scale; the volume of each class being the average volume of its constituent frequencies. It then formats this data for MIDI and writes it out to a user specified file.

# Usage

```
> audio-to-midi --help
usage: audio-to-midi [-h] [--output OUTPUT] [--time-quantum TIME_QUANTUM]
                     [--activation-level ACTIVATION_LEVEL] [--condense]
                     [--single-note]
                     infile

positional arguments:
  infile                The sound file to process.

optional arguments:
  -h, --help            show this help message and exit
  --output OUTPUT, -o OUTPUT
                        The MIDI file to output. Default: <infile>.mid
  --time-quantum TIME_QUANTUM, -t TIME_QUANTUM
                        The time span over which to compute the individual
                        FFTs in milliseconds.
  --activation-level ACTIVATION_LEVEL, -a ACTIVATION_LEVEL
                        The amplitude threshold for notes to be added to the
                        MIDI file. Must be between 0 and 1.
  --condense, -c        Combine contiguous notes at their average amplitude.
  --single-note, -s     Only add the loudest note to the MIDI file for a given
                        time span.
```
