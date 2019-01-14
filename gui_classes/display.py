import tkinter as tk
from math import floor
from PIL import ImageTk, Image
from tkinter import TclError
from .window import Window, get_ideal_size
from .presenter import Presenter


class Display(Window):
    """
    TODO: Write documentation
    """

    def setup_gui(self):
        """
        TODO: Write documentation
        """

        self.master.bind('s', self.open_presenter_view)
        self.master.bind('<Key>', self.show_key_info)

        self.canvas = tk.Canvas(self.frame, width=300, height=300)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.imgOrig = self.get_image_element('current')
        self.canvas.bind('<Configure>', self.configure)

        self.presenter = None
        self.app = None

    def configure(self, event):
        """
        TODO: Write documentation
        """

        self.canvas.delete('all')
        self.set_image_element(event.width, event.height)

    def open_presenter_view(self, event):
        """
        TODO: Write documentation
        """

        self.presenter = tk.Toplevel(self.master)
        self.app = Presenter(self.presenter, self, self.pages, self.slideNum)

    def show_key_info(self, event):
        """
        TODO: Write documentation
        """

        print(f'{event.char} / {event.keysym} / {event.keycode}')

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

    def set_image_element(self, width=None, height=None):
        """
        TODO: Write documentation
        """

        if width is None:
            width = self.master.winfo_width()

        if height is None:
            height = self.master.winfo_height()

        size = get_ideal_size(self.imgOrig.size, (width, height))

        if size[0] <= 0 or size[1] <= 0:
            return

        self.img = ImageTk.PhotoImage(
            self.imgOrig.copy().resize(size, resample=Image.HAMMING))
        self.canvas.create_image(0, 0, image=self.img, anchor=tk.NW)

    def on_update_slide(self, slideNum, fromElem=None):
        """
        TODO: Write documentation
        """

        if fromElem == self and self.presenter is not None:
            try:
                self.app.set_slide(slideNum, self)
            except TclError:
                print('Caught an error')

        self.imgOrig = self.get_image_element('current')
        self.set_image_element()
