import argparse
import sys

import gui
import pdftools


def main():
    parser = argparse.ArgumentParser(description='Process and view a PDF file')
    parser.add_argument('filename', type=str, metavar='FILENAME', nargs='?', help='name of PDF file to use', default=None)
    parser.add_argument('-n', '--nosplit', action='store_true', help='Do not perform split on files')

    args = parser.parse_args()
    print(args)

if __name__ == '__main__':
    main()