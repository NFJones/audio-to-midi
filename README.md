# audio-to-midi

`audio-to-midi` takes in a sound file and converts it to a multichannel MIDI file. It accomplishes this by performing FFT's on all channels of the audio data at user specified time steps. It then separates the resulting frequency analysis into equivalence classes which correspond to the twelve tone scale; the volume of each class being the average volume of its constituent frequencies. It then formats this data for MIDI and writes it out to a user specified file. It has the ability to convert whichever audio file formats are supported by the [soundfile](https://pypi.org/project/SoundFile/) module. libsndfile must be installed before running `audio-to-midi`

- [This is an example of a conversion using a time quantum of 5ms and an activation level of 0.](https://soundcloud.com/neil-jones/this-is-a-test)

## Installation

```
> python3 ./setup.py install
```

## Usage

```
> audio-to-midi --help
usage: audio-to-midi [-h] [--output OUTPUT] [--time-quantum TIME_QUANTUM]
                     [--activation-level ACTIVATION_LEVEL] [--condense]
                     [--single-note] [--no-progress]
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
  --no-progress, -n     Don't print the progress bar.
```
