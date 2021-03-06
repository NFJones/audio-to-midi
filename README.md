# audio-to-midi

`audio-to-midi` takes in a sound file and converts it to a multichannel MIDI file. It accomplishes this by performing FFT's on all channels of the audio data at user specified time steps. It then separates the resulting frequency analysis into equivalence classes which correspond to the twelve tone scale; the volume of each class being the average volume of its constituent frequencies. It then formats this data for MIDI and writes it out to a user specified file. It has the ability to convert whichever audio file formats are supported by the [soundfile](https://pypi.org/project/SoundFile/) module. libsndfile must be installed before running `audio-to-midi`

- [This is an example of a conversion using a time window of 5ms and an activation level of 0.](https://soundcloud.com/neil-jones/this-is-a-test)

## Installation

```
> python3 ./setup.py install
```

## Usage

```shell
> audio-to-midi --help
usage: audio-to-midi [-h] [--output OUTPUT] [--time-window TIME_WINDOW] [--activation-level ACTIVATION_LEVEL] [--condense]
                     [--condense-max] [--single-note] [--note-count NOTE_COUNT] [--bpm BPM] [--beat BEAT] [--transpose TRANSPOSE]
                     [--pitch-set PITCH_SET [PITCH_SET ...]] [--pitch-range PITCH_RANGE PITCH_RANGE] [--no-progress]
                     infile

positional arguments:
  infile                The sound file to process.

optional arguments:
  -h, --help            show this help message and exit
  --output OUTPUT, -o OUTPUT
                        The MIDI file to output. Default: <infile>.mid
  --time-window TIME_WINDOW, -t TIME_WINDOW
                        The time span over which to compute the individual FFTs in milliseconds.
  --activation-level ACTIVATION_LEVEL, -a ACTIVATION_LEVEL
                        The amplitude threshold for notes to be added to the MIDI file. Must be between 0 and 1.
  --condense, -c        Combine contiguous notes at their average amplitude.
  --condense-max, -m    Write the maximum velocity for a condensed note segment rather than the rolling average.
  --single-note, -s     Only add the loudest note to the MIDI file for a given time window.
  --note-count NOTE_COUNT, -C NOTE_COUNT
                        Only add the loudest n notes to the MIDI file for a given time window.
  --bpm BPM, -b BPM     Beats per minute. Defaults: 60
  --beat BEAT, -B BEAT  Time window in terms of beats (1/4, 1/8, etc.). Supercedes the time window parameter.
  --transpose TRANSPOSE, -T TRANSPOSE
                        Transpose the MIDI pitches by a constant offset.
  --pitch-set PITCH_SET [PITCH_SET ...], -p PITCH_SET [PITCH_SET ...]
                        Map to a pitch set. Values must be in the range: [0, 11]. Ex: -p 0 2 4 5 7 9 11
  --pitch-range PITCH_RANGE PITCH_RANGE, -P PITCH_RANGE PITCH_RANGE
                        The minimumand maximum allowed MIDI notes. These may be superseded by the calculated FFT range.
  --no-progress, -n     Don't print the progress bar.
```

## Example

```shell
>$ audio-to-midi ./this_is_a_test.wav -b 120 -t 30
./this_is_a_test.wav
samplerate: 44100 Hz
channels: 1
duration: 2.000 s
format: WAV (Microsoft) [WAV]
subtype: Signed 16 bit PCM [PCM_16]
window: 5.0 ms
frequencies: min = 200.0 Hz, max = 20000 Hz
100% (401 of 401) |##############################################################| Elapsed Time: 0:00:00 Time:  0:00:00
> ls ./*.mid
./this_is_a_test.wav.mid
```

## Docker Image

Build the docker file with
`docker build -t audio-to-midi-docker .`

Run any arguments to audio-to-midi like so
`docker run -v $(pwd):/myfiles -u 1000:1000 audio-to-midi /myfiles/{Input Wav file here} -o /myfiles/{output.mid} {anyotherargumentshere}`

