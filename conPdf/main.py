# -*- coding: utf-8 -*-
# Copyright (c) 2023 Jyrki Launonen

import argparse
import locale
import sys

from jinja2.exceptions import UndefinedError

from conPdf import compiler


def main():
    # Init locale.
    locale.setlocale(locale.LC_ALL, "")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "template",
        metavar="template.html",
        help="Template filename. CSS file with same base name is expected to be found beside it.",
    )
    parser.add_argument(
        "csv",
        metavar="data.csv",
        help="Input data. First row must contain header values.",
    )
    parser.add_argument(
        "--encoding",
        type=str,
        help="CSV encoding, if not default. e.g. iso-8859-15 or utf-8",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Output filename. If absent, will output to stdout.",
    )
    parser.add_argument(
        "--dblquote",
        action="store_true",
        default=False,
        help="Force double quoting to be used in CSV dialect.",
    )
    parser.add_argument(
        "--html",
        action="store_true",
        default=False,
        help="Instead of PDF, output an HTML intermediate.",
    )
    args = parser.parse_args()

    try:
        output = compiler.render(
            args.template,
            args.csv,
            args.encoding,
            args,
        )
    except (TypeError, UndefinedError) as e:
        print("Errors encountered, processing stopped:", e)
        exit(1)

    if args.output:
        mode = "wt" if args.html else "wb"
        with open(args.output, mode) as f:
            f.write(output)
    else:
        sys.stdout.write(output)
        sys.stdout.write("\n")


if __name__ == '__main__':
    main()
