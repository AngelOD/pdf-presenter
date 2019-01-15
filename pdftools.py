import subprocess
import os
import math
from queue import Queue
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
    """
    TODO: Write documentation
    """
    if not outputPath.exists():
        outputPath.mkdir(parents=True)


def clean_output_dir(outputPath):
    """
    TODO: Write documentation
    """
    files = os.listdir(outputPath)

    for name in files:
        f = outputPath / name

        if not f.is_file():
            continue

        f.unlink()


def get_pages(outputPath, spaces=4, fileType='png', useStoredImages=False):
    """
    TODO: Write documentation
    """
    pages = []

    def _addPage(slide, notes, pacing):
        nonlocal pages
        nonlocal useStoredImages

        if not useStoredImages:
            slide = Image.open(slide)
            slide.load()

            if type(notes) == str:
                notes = Image.open(notes)
                notes.load()

        pages.append({
            'slide': slide,
            'notes': notes,
            'pacing': pacing
        })

    files = os.listdir(outputPath)
    files.sort()

    for name in files:
        f = outputPath / name

        if (
            not f.is_file()
            or f.suffix != f'.{fileType}'
            or f.stem.endswith('-2')
        ):
            continue

        pacing = 120
        slide = str(f)
        notes = None

        if f.stem.endswith('-1'):
            notes = slide.replace('-1', '-2')

        _addPage(slide, notes, pacing)

    return pages


def convert_pdf_to_images(
    inputPath, outputPath, spaces=4, fileType='png', dpi=300
):
    """
    TODO: Write documentation
    """
    subprocess.run([
        'mutool', 'draw',
        '-o', str(outputPath / f'%0{spaces}d.{fileType}'),
        '-r', f'{dpi}',
        str(inputPath)
    ], stderr=subprocess.PIPE)


def prepare_images(outputPath, fileType='png', splitInHalf=True):
    """
    TODO: Write documentation
    """
    if not splitInHalf:
        return

    files = os.listdir(outputPath)

    for name in files:
        f = outputPath / name

        if not f.is_file() or f.suffix != f'.{fileType}':
            continue

        try:
            im = Image.open(f)

            if not splitInHalf:
                continue
            elif f.stem.endswith('-1') or f.stem.endswith('-2'):
                # Images have already been split and are stored as files
                continue

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

            if w > h:
                x1 = x2 + 1
                x2 = w
            else:
                y1 = y2 + 1
                y2 = h

            box = (x1, y1, x2, y2)
            part2 = im.crop(box)

            part1.save(outputPath.joinpath(f.stem + '-1' + f.suffix))
            part2.save(outputPath.joinpath(f.stem + '-2' + f.suffix))
            f.unlink()
        except IOError:
            print(f'Something went wrong while processing {f}')
