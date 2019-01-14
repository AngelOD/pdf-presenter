import tkinter as tk
from math import floor
from PIL import Image


class Window:
    """
    TODO: Write documentation
    """

    def __init__(self, master, pages):
        """
        TODO: Write documentation
        """

        self.master = master
        self.frame = tk.Frame(self.master)
        self.is_fullscreen = False
        self.pages = pages
        self.prev_geom = '300x300+100+100'
        self.slideNum = 0

        master.bind('<Escape>', self.exit_fullscreen)
        master.bind('b', self.toggle_fullscreen)
        master.bind('<Destroy>', self.handle_destroy)
        master.bind('<Next>', self.next_slide)
        master.bind('<Prior>', self.prev_slide)

        self.setup_gui()

        self.frame.pack(fill=tk.BOTH, expand=True)

    def exit_fullscreen(self, event):
        """
        TODO: Write documentation
        """

        if self.is_fullscreen:
            self.toggle_fullscreen(event)

    def get_image_element(self, imageType='current'):
        """
        TODO: Write documentation
        """

        image = None

        if imageType == 'current':
            slide = self.pages[self.slideNum]['slide']

            if type(slide) == str:
                image = Image.open(slide)
            else:
                image = slide
        elif imageType == 'next':
            if self.slideNum + 1 < len(self.pages):
                slide = self.pages[self.slideNum + 1]['slide']

                if type(slide) == str:
                    image = Image.open(slide)
                else:
                    image = slide
        elif imageType == 'notes':
            if self.pages[self.slideNum]['notes'] is not None:
                notes = self.pages[self.slideNum]['notes']

                if type(notes) == str:
                    image = Image.open(notes)
                else:
                    image = notes

        if image is not None:
            image.load()

        return image

    def get_pacing(self):
        """
        TODO: Write documentation
        """

        return self.pages[self.slideNum]['pacing']

    def get_pacing_begin(self):
        """
        TODO: Write documentation
        """

        return self.pages[self.slideNum]['pacingStart']

    def get_pacing_end(self):
        """
        TODO: Write documentation
        """

        return self.get_pacing_begin() + self.get_pacing()

    def get_time_parts(self, diff):
        """
        TODO: Write documentation
        """

        m = floor((diff // 60) % 60)
        h = floor(diff // 3600)
        s = floor(diff % 60)

        return (h, m, s)

    def toggle_fullscreen(self, event):
        """
        TODO: Write documentation
        """

        self.is_fullscreen = not self.is_fullscreen
        self.master.overrideredirect(self.is_fullscreen)

        if self.is_fullscreen:
            self.prev_geom = self.master.wm_geometry()
            self.master.wm_state('zoomed')
        else:
            self.master.wm_state('normal')
            self.master.wm_geometry(self.prev_geom)

    def prev_slide(self, event):
        """
        TODO: Write documentation
        """

        self.slideNum = max(self.slideNum - 1, 0)
        self.on_update_slide(self.slideNum, self)

    def next_slide(self, event):
        """
        TODO: Write documentation
        """

        self.slideNum = min(self.slideNum + 1, len(self.pages) - 1)
        self.on_update_slide(self.slideNum, self)

    def set_slide(self, slideNum, fromElem=None):
        """
        TODO: Write documentation
        """

        if slideNum < 0:
            slideNum = 0

        self.slideNum = min(slideNum, len(self.pages))
        self.on_update_slide(self.slideNum, fromElem)

    def handle_destroy(self, event):
        """
        TODO: Write documentation
        """

        self.on_destroy()

    def setup_gui(self):
        """
        TODO: Write documentation
        """

        pass

    def on_destroy(self):
        """
        TODO: Write documentation
        """

        pass

    def on_update_slide(self, slideNum, fromElem=None):
        """
        TODO: Write documentation
        """

        pass


def get_ideal_size(original, desired):
    ratioOrig = original[0] / original[1]
    ratioDes = desired[0] / desired[1]

    if ratioDes > ratioOrig:
        return (floor(original[0] * (desired[1] / original[1])), desired[1])
    else:
        return (desired[0], floor(original[1] * (desired[0] / original[0])))
