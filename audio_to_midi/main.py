import argparse
import soundfile
import os
import numpy
import sys
import threading
import time

from audio_to_midi import converter


def progress_bar(progress_cb):
    current = 0
    total = 100

    while True:
        current, total = progress_cb()
        percentage = (current / total) * 100

        bar_width = int((current / total) * 80)
        space_width = 80 - bar_width
        sys.stdout.write(
            "\r|{}{}| {:.2f}%".format("=" * bar_width, " " * space_width, percentage)
        )

        time.sleep(0.1)

        if int(percentage) == 100:
            break
    print()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("infile", help="The sound file to process.")
    parser.add_argument(
        "--output", "-o", help="The MIDI file to output. Default: <infile>.mid"
    )
    parser.add_argument(
        "--time-quantum",
        "-t",
        default=5.0,
        type=float,
        help="The time span over which to compute the individual FFTs in milliseconds.",
    )
    parser.add_argument(
        "--activation-level",
        "-a",
        default=0.0,
        type=float,
        help="The amplitude threshold for notes to be added to the MIDI file. Must be between 0 and 1.",
    )
    parser.add_argument(
        "--condense",
        "-c",
        action="store_true",
        help="Combine contiguous notes at their average amplitude.",
    )
    parser.add_argument(
        "--single-note",
        "-s",
        action="store_true",
        help="Only add the loudest note to the MIDI file for a given time span.",
    )
    args = parser.parse_args()

    args.output = (
        "{}.mid".format(os.path.basename(args.infile))
        if not args.output
        else args.output
    )

    samples, samplerate = soundfile.read(args.infile)

    if isinstance(samples[0], numpy.float64):
        samples = [[s] for s in samples]

    current = 0
    total = len(samples)

    def set_progress(c, t):
        nonlocal current
        nonlocal total

        current = c
        total = t

    def get_progress():
        nonlocal current
        nonlocal total
        return current, total

    progress_thread = threading.Thread(target=progress_bar, args=(get_progress,))
    progress_thread.start()

    process = converter.Converter(
        samples=samples,
        channels=len(samples[0]),
        samplerate=samplerate,
        time_quantum=args.time_quantum,
        activation_level=args.activation_level,
        condense=args.condense,
        single_note=args.single_note,
        outfile=args.output,
        progress_callback=set_progress,
    )
    process.convert()

    progress_thread.join()


if __name__ == "__main__":
    main()
