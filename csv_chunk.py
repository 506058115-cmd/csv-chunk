#!/usr/bin/env python3
"""Split a CSV table into row-limited files without loading it all into memory."""

import argparse
import csv
import sys
import tempfile
from pathlib import Path


def positive_int(value):
    try:
        number = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be a positive integer") from error
    if number < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def main():
    parser = argparse.ArgumentParser(
        description="Split a CSV file into smaller files, repeating its header in each part."
    )
    parser.add_argument("input", type=Path, help="CSV file to split")
    parser.add_argument(
        "--rows-per-file", type=positive_int, default=10000,
        help="data rows per output file (default: 10000)",
    )
    parser.add_argument(
        "--delimiter", default=",", help="one-character CSV delimiter (default: comma)"
    )
    parser.add_argument(
        "--output-dir", type=Path,
        help="new directory for the parts (default: INPUT-stem-parts)",
    )
    args = parser.parse_args()
    if len(args.delimiter) != 1:
        parser.error("--delimiter must be exactly one character")

    source = args.input.expanduser()
    if not source.is_file():
        parser.error(f"input file not found: {source}")
    source = source.resolve()
    output_dir = args.output_dir.expanduser() if args.output_dir else source.with_name(f"{source.stem}-parts")
    if output_dir.exists() or output_dir.is_symlink():
        parser.error(f"refusing to use existing output directory: {output_dir}")
    output_dir = output_dir.resolve()

    try:
        output_dir.parent.mkdir(parents=True, exist_ok=True)
        with source.open("r", encoding="utf-8-sig", newline="") as input_file:
            reader = csv.reader(input_file, delimiter=args.delimiter)
            try:
                header = next(reader)
            except StopIteration:
                parser.error("input file is empty; a header row is required")

            with tempfile.TemporaryDirectory(
                prefix=f".{output_dir.name}.tmp-", dir=output_dir.parent
            ) as temporary:
                staging = Path(temporary)
                part_number = 1
                rows_in_part = 0

                def open_part(number):
                    output = (staging / f"{source.stem}-part-{number:04d}.csv").open(
                        "w", encoding="utf-8", newline=""
                    )
                    writer = csv.writer(output, delimiter=args.delimiter)
                    writer.writerow(header)
                    return output, writer

                part_file, writer = open_part(part_number)
                try:
                    for row in reader:
                        if rows_in_part == args.rows_per_file:
                            part_file.close()
                            part_number += 1
                            rows_in_part = 0
                            part_file, writer = open_part(part_number)
                        writer.writerow(row)
                        rows_in_part += 1
                finally:
                    part_file.close()

                staging.rename(output_dir)
    except (OSError, csv.Error, UnicodeError) as error:
        print(f"csv-chunk: {error}", file=sys.stderr)
        return 2

    print(f"Wrote {part_number} part(s) to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
