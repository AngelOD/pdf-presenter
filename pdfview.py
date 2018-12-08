import argparse
import os
import sys
from pathlib import Path

import gui
import pdftools


def main():
    parser = argparse.ArgumentParser(description='Process and view a PDF file')

    parser.add_argument('filename', type=str, metavar='FILENAME', nargs='?', help='name of PDF file to use', default=None)
    parser.add_argument('--dpi', type=int, metavar='DPI', nargs=1, help='The DPI to use for the pages (default=240)', default=240)
    parser.add_argument('-n', '--nosplit', action='store_true', help='Do not perform split on files')
    parser.add_argument('-o', '--output', type=str, metavar='OUTPUT_DIR', nargs=1, help='The output directory (default=\'./output\')', default='./output')
    parser.add_argument('-l', '--left', action='store_true', help='Notes are on the left instead of the right')

    args = parser.parse_args()
    outputPath = Path(args.output)

    pdftools.ensure_output_path(outputPath)

    if args.filename is not None:
        if not pdftools.locate_mutool():
            print('You need the mutool executable in the current working directory.')
            sys.exit(2)

        inputPath = Path(args.filename)

        if not inputPath.exists():
            print('Input file does not exist.')
            sys.exit(2)

        print('Preparing files. Please wait...', flush=True)
        pdftools.clean_output_dir(outputPath)
        pdftools.convert_pdf_to_images(inputPath, outputPath, dpi=args.dpi)

        if not args.nosplit:
            pdftools.split_images_in_half(outputPath)

        print(f'Files ready!', flush=True)

    pages = pdftools.get_pages(outputPath)

    print(f'Found {len(pages)} pages. Starting viewer...', flush=True)

    gui.main(pages)


if __name__ == '__main__':
    main()