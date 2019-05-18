import argparse
import soundfile
import os

from audio_to_midi import fft


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("infile")
    parser.add_argument("--output", "-o")
    parser.add_argument("--time-quantum", "-t", default=10.0, type=float)
    parser.add_argument("--activation-level", "-a", default=0.2, type=float)
    parser.add_argument("--condense", "-c", action="store_true")
    parser.add_argument("--single-note", "-s", action="store_true")
    args = parser.parse_args()

    args.output = (
        "{}.mid".format(os.path.basename(args.infile))
        if not args.output
        else args.output
    )

    samples, samplerate = soundfile.read(args.infile)

    f = fft.FFT(
        samples=samples,
        channels=len(samples[0]),
        samplerate=samplerate,
        time_quantum=args.time_quantum,
        activation_level=args.activation_level,
        condense=args.condense,
        single_note=args.single_note,
        outfile=args.output,
    )
    f.calculate()


if __name__ == "__main__":
    main()
