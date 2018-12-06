import subprocess
import os
import math
from pathlib import Path
from PIL import Image


def locate_mutool():
    """
        Checks for the presence of mutool and if found, returns the Path
        object for it. If not it returns False.
    """
    f1, f2 = Path('./mutool'), Path('./mutool.exe')

    if f1.exists():
        return f1
    elif f2.exists():
        return f2

    return False


def ensure_output_path(outputPath):
    if not outputPath.exists():
        outputPath.mkdir(parents=True)


def clean_output_dir(outputPath):
    files = os.listdir(outputPath)

    for name in files:
        f = outputPath / name

        if not f.is_file():
            continue

        f.unlink()


def convert_pdf_to_images(
    inputPath, outputPath, prefix='page', spaces=4, type='png', dpi=120
):
    subprocess.call([
        'mutool', 'draw',
        '-o', str(outputPath / f'{prefix}%0{spaces}d.{type}'),
        '-r', f'{dpi}',
        str(inputPath)
    ])


def split_images_in_half(outputPath, type='png', removeAfter=True):
    files = os.listdir(outputPath)

    for name in files:
        f = outputPath / name

        if not f.is_file() or f.suffix != f'.{type}':
            continue

        try:
            im = Image.open(f)
            x1 = 0
            y1 = 0
            w = im.width
            h = im.height

            if w > h:
                x2 = math.floor(w / 2) - 1
                y2 = h
            else:
                x2 = w
                y2 = math.floor(h / 2) - 1

            box = (x1, y1, x2, y2)
            part1 = im.crop(box)
            part1.save(outputPath.joinpath(f.stem + '-1' + f.suffix))

            if w > h:
                x1 = x2 + 1
                x2 = w
            else:
                y1 = y2 + 1
                y2 = h

            box = (x1, y1, x2, y2)
            part2 = im.crop(box)
            part2.save(outputPath.joinpath(f.stem + '-2' + f.suffix))

            if removeAfter:
                f.unlink()
        except IOError:
            print(f'Something went wrong while processing {f}')
