#!/usr/bin/env python3

import argparse
import os
import sys
import logging

from audio_to_midi import converter, progress_bar


def parse_args():
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
        "--bpm", "-b", type=int, help="Beats per minute. Defaults: 60", default=60
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

    if args.single_note:
        args.note_count = 1

    return args


def main():
    try:
        logging.basicConfig(level=logging.DEBUG, format="%(message)s")

        args = parse_args()

        progress = progress_bar.ProgressBar()

        def set_progress(current, total):
            if not args.no_progress:
                progress.update(current=current, total=total)

        process = converter.Converter(
            infile=args.infile,
            outfile=args.output,
            time_window=args.time_window,
            activation_level=args.activation_level,
            condense=args.condense,
            note_count=args.note_count,
            progress_callback=set_progress,
            bpm=args.bpm,
        )
        process.convert()
        progress.stop()
    except KeyboardInterrupt:
        progress.stop()
        sys.exit(1)
    except Exception as e:
        progress.stop()
        logging.exception(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
