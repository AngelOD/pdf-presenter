import time
import tkinter as tk
from math import floor
from threading import Event, Thread
from tkinter import font as tkfont
from PIL import ImageTk, Image
from .window import Window, get_ideal_size


class Presenter(Window):
    """
    TODO: Write documentation
    """

    def __init__(self, master, parent, pages, slideNum):
        """
        TODO: Write documentation
        """

        super().__init__(master, pages)

        self.parent = parent
        self.slideNum = slideNum
        self.images = {}
        self.orgImages = {
            'current': self.get_image_element('current'),
            'next': self.get_image_element('next'),
            'notes': self.get_image_element('notes'),
        }

        self.startTime = time.time()
        self.stopFlag = Event()
        self.timer = TimerThread(self.stopFlag, self.update_time)

        defaultFont = tkfont.Font(
            family='Helvetica',
            size=30,
            weight='normal'
        )

        self.fontCurrent = defaultFont
        self.fontElapsed = defaultFont
        self.fontPacing = defaultFont
        self.current_timer = None
        self.elapsed_timer = None
        self.pacing_timer = None
        self.lastCurrent = ''
        self.lastElapsed = ''
        self.lastPacing = ''

        self.timer.start()

    def setup_gui(self):
        """
        TODO: Write documentation
        """

        self.frame['bg'] = 'gray70'

        self.canvas_current = tk.Canvas(self.frame, height=200)
        self.canvas_next = tk.Canvas(self.frame, height=200)
        self.canvas_timer = tk.Canvas(self.frame, height=200)
        self.canvas_notes = tk.Canvas(self.frame, height=200)

        self.canvas_current['bg'] = 'gray20'
        self.canvas_next['bg'] = 'gray30'
        self.canvas_notes['bg'] = 'gray20'

        stickyAll = tk.N + tk.S + tk.E + tk.W

        self.canvas_current.grid(row=0, column=0, sticky=stickyAll)
        self.canvas_next.grid(row=1, column=0, sticky=stickyAll)
        self.canvas_notes.grid(row=1, column=1, sticky=stickyAll)
        self.canvas_timer.grid(row=0, column=1, sticky=stickyAll)

        self.canvas_current.bind('<Configure>', self.configureCurrent)
        self.canvas_next.bind('<Configure>', self.configureNext)
        self.canvas_notes.bind('<Configure>', self.configureNotes)
        self.canvas_timer.bind('<Configure>', self.configureTimer)

        self.canvas_timer.bind('<ButtonPress-1>', self.onClickTimer)

        # Configure rows and columns
        for i in range(2):
            self.frame.rowconfigure(i, weight=1, minsize=150)
            self.frame.columnconfigure(i, weight=1)

    def configureCurrent(self, event):
        """
        TODO: Write documentation
        """

        self.configureGeneric('current')

    def configureNext(self, event):
        """
        TODO: Write documentation
        """

        self.configureGeneric('next')

    def configureNotes(self, event):
        """
        TODO: Write documentation
        """

        self.configureGeneric('notes')

    def configureGeneric(self, type):
        """
        TODO: Write documentation
        """

        canvas = self.get_canvas_element(type)

        if canvas is None:
            return

        canvas.delete('all')
        self.set_image_element(canvas, self.orgImages[type], type)

    def configureTimer(self, event):
        """
        TODO: Write documentation
        """

        height = event.height

        if height < 150:
            fsElapsed = 34
            fsPacing = 22
            fsCurrent = 46
        elif height < 225:
            fsElapsed = 40
            fsPacing = 30
            fsCurrent = 46
        else:
            fsElapsed = 70
            fsPacing = 50
            fsCurrent = 80

        self.fontCurrent = tkfont.Font(
            family='Helvetica',
            size=fsCurrent,
            weight='bold'
        )
        self.fontElapsed = tkfont.Font(
            family='Helvetica',
            size=fsElapsed,
            weight='bold'
        )
        self.fontPacing = tkfont.Font(
            family='Helvetica',
            size=fsPacing,
            weight='normal'
        )

        self.lastCurrent = ''
        self.lastElapsed = ''
        self.lastPacing = ''

        self.update_time()

    def get_canvas_element(self, type):
        """
        TODO: Write documentation
        """

        if type == 'current':
            return self.canvas_current
        elif type == 'next':
            return self.canvas_next
        elif type == 'notes':
            return self.canvas_notes

        return None

    def onClickTimer(self, event):
        """
        TODO: Write documentation
        """

        self.startTime = floor(time.time() - self.get_pacing_begin())
        self.update_time()

    def set_image_element(self, canvas, image, saveSlot):
        """
        TODO: Write documentation
        """

        if image is None:
            return

        width = canvas.winfo_width()
        height = canvas.winfo_height()

        size = get_ideal_size(image.size, (width, height))

        if size[0] <= 0 or size[1] <= 0:
            return

        img = ImageTk.PhotoImage(
            image.copy().resize(size, resample=Image.HAMMING))

        self.images[saveSlot] = img

        canvas.create_image(0, 0, image=img, anchor=tk.NW)

    def update_time(self):
        """
        TODO: Write documentation
        """

        prefix = ''
        width, height = (
            self.canvas_timer.winfo_width(),
            self.canvas_timer.winfo_height()
        )

        # Define the clock
        clockPrint = time.strftime('%H:%M')

        # Define the elapsed timer
        tdiff = floor(time.time() - self.startTime)
        h, m, s = self.get_time_parts(tdiff)

        if h > 0:
            prefix = f'{str(h).zfill(2)}:'

        elapsedPrint = f'{prefix}{str(m).zfill(2)}:{str(s).zfill(2)}'

        # Define the pacing timer including the colour
        pdiff = floor(self.get_pacing_end() - tdiff)
        h, m, s = self.get_time_parts(abs(pdiff))
        if pdiff >= 0:
            prefix = ''

            if pdiff > self.get_pacing():
                pfill = 'blue'
            else:
                pfill = 'green'
        else:
            prefix = '-'
            pfill = 'red'

        if h > 0:
            prefix = f'{prefix}{str(h).zfill(2)}:'

        pacingPrint = f'{prefix}{str(m).zfill(2)}:{str(s).zfill(2)}'

        # Figure out what needs updating and update accordingly
        updateCurrent = clockPrint != self.lastCurrent
        updateElapsed = elapsedPrint != self.lastElapsed
        updatePacing = pacingPrint != self.lastPacing

        if updateCurrent:
            self.lastCurrent = clockPrint

            if hasattr(self, 'current_timer'):
                self.canvas_timer.delete(self.current_timer)

            self.current_timer = self.canvas_timer.create_text(
                width-10, floor(height // 2),
                fill='black',
                anchor=tk.E,
                font=self.fontCurrent,
                text=clockPrint
            )

        if updateElapsed:
            self.lastElapsed = elapsedPrint

            if hasattr(self, 'elapsed_timer'):
                self.canvas_timer.delete(self.elapsed_timer)

            self.elapsed_timer = self.canvas_timer.create_text(
                10, 10,
                fill='blue',
                anchor=tk.NW,
                font=self.fontElapsed,
                text=elapsedPrint
            )

        if updatePacing:
            self.lastPacing = pacingPrint

            if hasattr(self, 'pacing_timer'):
                self.canvas_timer.delete(self.pacing_timer)

            self.pacing_timer = self.canvas_timer.create_text(
                10, height-10,
                fill=pfill,
                anchor=tk.SW,
                font=self.fontPacing,
                text=pacingPrint
            )

    def on_destroy(self):
        """
        TODO: Write documentation
        """

        self.stopFlag and self.stopFlag.set()
        self.parent = None

    def on_update_slide(self, slideNum, fromElem=None):
        """
        TODO: Write documentation
        """

        if fromElem == self:
            self.parent.set_slide(slideNum, self)

        for elem in ('current', 'next', 'notes'):
            canvas = self.get_canvas_element(elem)
            self.orgImages[elem] = self.get_image_element(elem)
            self.set_image_element(canvas, self.orgImages[elem], elem)

        self.set_image_element(
            self.canvas_current,
            self.orgImages['current'],
            'current'
        )


class TimerThread(Thread):
    """
    TODO: Write documentation
    """

    def __init__(self, event, callback):
        Thread.__init__(self)

        self.stopped = event
        self.callback = callback

    def run(self):
        while not self.stopped.wait(1):
            self.callback()
