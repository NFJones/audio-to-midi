#!/usr/bin/env python3

import argparse
import os
import sys
import logging

from audio_to_midi import converter, progress_bar


def _convert_beat_to_time(bpm, beat):
    try:
        parts = beat.split("/")
        if len(parts) > 2:
            raise Exception()

        beat = [int(part) for part in parts]
        fraction = beat[0] / beat[1]
        bps = bpm / 60
        ms_per_beat = bps * 1000
        return fraction * ms_per_beat
    except Exception:
        raise RuntimeError("Invalid beat format: {}".format(beat))


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
        "--condense-max",
        "-m",
        action="store_true",
        help="Write the maximum velocity for a condensed note segment rather than the rolling average.",
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
        "--beat",
        "-B",
        help="Time window in terms of beats (1/4, 1/8, etc.). Supercedes the time window parameter.",
    )
    parser.add_argument(
        "--transpose",
        "-T",
        type=int,
        default=0,
        help="Transpose the MIDI pitches by a constant offset.",
    )
    parser.add_argument(
        "--key", "-k", type=int, nargs="+", default=[], help="Map to a pitch set."
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

    if args.key:
        for key in args.key:
            if key not in range(12):
                raise RuntimeError("Key values must be in the range: [0, 12)")

    if args.beat:
        args.time_window = _convert_beat_to_time(args.bpm, args.beat)
        print(args.time_window)

    return args


def main():
    try:
        logging.basicConfig(level=logging.DEBUG, format="%(message)s")

        args = parse_args()

        process = converter.Converter(
            infile=args.infile,
            outfile=args.output,
            time_window=args.time_window,
            activation_level=args.activation_level,
            condense=args.condense,
            condense_max=args.condense_max,
            note_count=args.note_count,
            transpose=args.transpose,
            key=args.key,
            progress=None if args.no_progress else progress_bar.ProgressBar(),
            bpm=args.bpm,
        )
        process.convert()
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception as e:
        logging.exception(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
