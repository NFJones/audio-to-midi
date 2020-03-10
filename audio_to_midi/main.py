import argparse
import soundfile
import os
import numpy
import sys
import threading
import time
import progressbar

from audio_to_midi import converter


def progress_bar(progress_cb):
    current, total = progress_cb()

    with progressbar.ProgressBar(max_value=total) as progress:
        while True:
            current, total = progress_cb()
            progress.update(current)
            time.sleep(0.1)
            if current == total:
                break

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("infile", help="The sound file to process.")
    parser.add_argument(
        "--output", "-o", help="The MIDI file to output. Default: <infile>.mid"
    )
    parser.add_argument(
        "--time-window",
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
        help="Only add the loudest note to the MIDI file for a given time window.",
    )
    parser.add_argument(
        "--note-count",
        "-C",
        type=int,
        default=0,
        help="Only add the loudest n notes to the MIDI file for a given time window.",
    )
    parser.add_argument(
        "--no-progress", "-n", action="store_true", help="Don't print the progress bar."
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

    print("Converting: {}".format(args.infile))

    if not args.no_progress:
        progress_thread = threading.Thread(target=progress_bar, args=(get_progress,))
        progress_thread.start()
    
    if args.single_note:
        args.note_count = 1

    process = converter.Converter(
        samples=samples,
        channels=len(samples[0]),
        samplerate=samplerate,
        time_window=args.time_window,
        activation_level=args.activation_level,
        condense=args.condense,
        note_count=args.note_count,
        outfile=args.output,
        progress_callback=set_progress,
    )
    process.convert()

    if not args.no_progress:
        progress_thread.join()


if __name__ == "__main__":
    main()
