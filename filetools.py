import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageTk


_breakingPoint = 75
_lookBackDist = 20


def parse_notes_file(notesFile, fileCount):
    """
    TODO: Write documentation
    """

    noteImages = [None for i in range(fileCount)]
    notes = [[] for i in range(fileCount)]
    nFile = Path(notesFile)

    if nFile.exists():
        with open(nFile) as json_file:
            data = json.load(json_file)

            for n in data['notes']:
                if len(n) < 2:
                    continue

                if n[0] >= 0 and n[0] < fileCount:
                    if isinstance(n[1], list):
                        for note in n[1]:
                            _add_note(notes[n[0]], note)
                    else:
                        for i in range(1, len(n)):
                            _add_note(notes[n[0]], n[i])

    # Generate notes images
    fnt = ImageFont.truetype('monofonto.ttf', size=32)
    for idx, notelist in enumerate(notes):
        if len(notelist) == 0:
            continue

        # Create image, draw surface and font
        img = Image.new('L', (1280, 720), 200)
        imgDraw = ImageDraw.Draw(img)

        # Write notes onto page
        s = '\n'.join(notelist)
        tSize = imgDraw.multiline_textsize(s, font=fnt)
        textPos = (30, (img.size[1] / 2) - (tSize[1] / 2))
        imgDraw.multiline_text(textPos, s, fill='black', font=fnt)

        # Add image to list at specific index
        noteImages[idx] = img

    return noteImages


def parse_pacing_file(pacingFile, fileCount):
    """
    TODO: Write documentation
    """
    pacings = [120 for i in range(fileCount)]
    pFile = Path(pacingFile)

    if not pFile.exists():
        return pacings

    with open(pFile) as json_file:
        data = json.load(json_file)

        for p in data['pacings']:
            if len(p) == 2 and len(p) >= 0 and p[0] < fileCount:
                pacings[p[0]] = p[1]
            elif len(p) == 3 and p[0] >= 0 and p[0] < p[1]:
                for i in range(p[0], min(p[1] + 1, fileCount)):
                    if i < fileCount:
                        pacings[i] = p[2]

    return pacings


def _add_note(notes, note):
    global _breakingPoint, _lookBackDist

    if not isinstance(note, str):
        return

    if not note.startswith('· '):
        note = f'· {note}'

    if len(note) > _breakingPoint:
        rest = note

        while len(rest) > _breakingPoint:
            i = rest.find(' ', _breakingPoint-_lookBackDist, _breakingPoint+1)

            if i == -1:
                i = _breakingPoint
                entry = f'{rest[:i]}-'
            else:
                entry = rest[:i]

            notes.append(entry)
            rest = f'  {rest[i:].lstrip()}'

        if len(rest) > 0:
            notes.append(rest)
    else:
        notes.append(note)
