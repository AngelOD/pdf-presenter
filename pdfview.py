import argparse
import os
import sys
from pathlib import Path

import gui
import pdftools


def _parseArgs():
    parser = argparse.ArgumentParser(description='Process and view a PDF file')

    parser.add_argument('filename', type=str, metavar='FILENAME', nargs='?', help='name of PDF file to use', default=None)
    parser.add_argument('--dpi', type=int, metavar='DPI', nargs=1, help='The DPI to use for the pages (default=240)', default=240)
    parser.add_argument('--files', action='store_true', help='Use files instead of keeping images in memory')
    parser.add_argument('--left', action='store_true', help='Notes are on the left instead of the right')
    parser.add_argument('--nosplit', action='store_true', help='Do not perform split on files')
    parser.add_argument('-o', '--output', type=str, metavar='OUTPUT_DIR', nargs=1, help='The output directory (default=\'./output\')', default='./output')

    return parser.parse_args()


def main():
    args = _parseArgs()
    outputPath = Path(args.output)

    pdftools.ensure_output_path(outputPath)

    if args.filename is not None:
        if not pdftools.locate_mutool():
            print('You need the mutool executable in the current working directory.')
            print('Download page: https://mupdf.com/downloads/index.html')
            sys.exit(2)

        inputPath = Path(args.filename)

        if not inputPath.exists():
            print('Input file does not exist.')
            sys.exit(2)

        print('Preparing files. Please wait...', flush=True)
        pdftools.clean_output_dir(outputPath)
        pdftools.convert_pdf_to_images(inputPath, outputPath, dpi=args.dpi)
        pdftools.prepare_images(outputPath, splitInHalf=not args.nosplit)
        print(f'Files ready!', flush=True)
    else:
        print('Loading images into memory...', flush=True)
        pdftools.prepare_images(outputPath, splitInHalf=not args.nosplit)

    pages = pdftools.get_pages(outputPath, useStoredImages=args.files)

    print(f'Found {len(pages)} pages. ', flush=True, end='')

    if len(pages) > 0:
        print('Starting viewer...', flush=True)
        gui.main(pages)
    else:
        print('Nothing to display!')


if __name__ == '__main__':
    main()