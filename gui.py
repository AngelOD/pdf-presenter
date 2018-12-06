import sys
import time
import tkinter as tk
from tkinter import font as tkfont
from math import floor
from threading import Event, Thread
from PIL import ImageTk, Image, ImageDraw, ImageFont


class Window:
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master)
        self.is_fullscreen = False
        self.prev_geom = '300x300+100+100'

        master.bind('<Escape>', self.exit_fullscreen)
        master.bind('b', self.toggle_fullscreen)
        master.bind('<Destroy>', self.handle_destroy)

        self.setup_gui()

        self.frame.pack(fill=tk.BOTH, expand=True)

    def exit_fullscreen(self, event):
        if self.is_fullscreen:
            self.toggle_fullscreen(event)

    def toggle_fullscreen(self, event):
        self.is_fullscreen = not self.is_fullscreen
        self.master.overrideredirect(self.is_fullscreen)

        if self.is_fullscreen:
            self.prev_geom = self.master.wm_geometry()
            self.master.wm_state('zoomed')
        else:
            self.master.wm_state('normal')
            self.master.wm_geometry(self.prev_geom)

    def handle_destroy(self, event):
        self.on_destroy()

    def setup_gui(self):
        pass

    def on_destroy(self):
        pass


class Display(Window):
    def setup_gui(self):
        self.master.bind('s', self.open_presenter_view)
        self.master.bind('<Key>', self.show_key_info)

        self.canvas = tk.Canvas(self.frame, width=300, height=300)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.imgOrig = Image.open('test30.png')
        self.canvas.bind('<Configure>', self.configure)

        self.presenter = None
        self.app = None

    def configure(self, event):
        self.canvas.delete('all')
        self.set_image(event.width, event.height)

    def open_presenter_view(self, event):
        self.presenter = tk.Toplevel(self.master)
        self.app = Presenter(self.presenter)

    def show_key_info(self, event):
        print(f'{event.char} / {event.keysym} / {event.keycode}')

    def toggle_fullscreen(self, event):
        self.is_fullscreen = not self.is_fullscreen
        self.master.overrideredirect(self.is_fullscreen)

        if self.is_fullscreen:
            self.prev_geom = self.master.wm_geometry()
            self.master.wm_state('zoomed')
        else:
            self.master.wm_state('normal')
            self.master.wm_geometry(self.prev_geom)

    def set_image(self, width, height):
        size = get_ideal_size(self.imgOrig.size, (width, height))

        if size[0] <= 0 or size[1] <= 0:
            return

        self.img = ImageTk.PhotoImage(
            self.imgOrig.copy().resize(size, resample=Image.HAMMING))
        self.canvas.create_image(0, 0, image=self.img, anchor=tk.NW)


class Presenter(Window):
    def __init__(self, master):
        super().__init__(master)

        self.startTime = time.time()
        self.slideTimes = (time.time(), time.time())
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

        self.lastCurrent = ''
        self.lastElapsed = ''
        self.lastPacing = ''

        self.timer.start()

    def setup_gui(self):
        self.frame['bg'] = 'orange'

        self.canvas_current = tk.Canvas(self.frame, height=200)
        self.canvas_next = tk.Canvas(self.frame, height=200)
        self.canvas_timer = tk.Canvas(self.frame, height=200)
        self.canvas_notes = tk.Canvas(self.frame, height=200)

        self.canvas_current['bg'] = 'red'
        self.canvas_next['bg'] = 'green'
        self.canvas_notes['bg'] = 'yellow'

        stickyAll = tk.N + tk.S + tk.E + tk.W

        self.canvas_current.grid(row=0, column=0, sticky=stickyAll)
        self.canvas_next.grid(row=1, column=0, sticky=stickyAll)
        self.canvas_timer.grid(row=0, column=1, sticky=stickyAll)
        self.canvas_notes.grid(row=1, column=1, sticky=stickyAll)

        self.canvas_timer.bind('<Configure>', self.configure)

        # Configure rows and columns
        for i in range(2):
            self.frame.rowconfigure(i, weight=1, minsize=150)
            self.frame.columnconfigure(i, weight=1)

    def configure(self, event):
        height = self.canvas_timer.winfo_height()

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

    def update_time(self):
        prefix = ''
        width, height = (self.canvas_timer.winfo_width(), self.canvas_timer.winfo_height())
        tdiff = floor(time.time() - self.startTime)
        m = floor((tdiff // 60) % 60)
        h = floor(tdiff // 3600)
        s = floor(tdiff % 60)

        if h > 0:
            prefix = f'{str(h).zfill(2)}:'

        clockPrint = time.strftime('%H:%M')
        timePrint = f'{prefix}{str(m).zfill(2)}:{str(s).zfill(2)}'

        updateCurrent = clockPrint != self.lastCurrent
        updateElapsed = timePrint != self.lastElapsed
        updatePacing = timePrint != self.lastPacing

        if updateCurrent:
            if hasattr(self, 'current_time'):
                self.canvas_timer.delete(self.current_time)

            self.current_time = self.canvas_timer.create_text(
                width-10, floor(height // 2),
                fill='black',
                anchor=tk.E,
                font=self.fontCurrent,
                text=clockPrint
            )

        if updateElapsed:
            if hasattr(self, 'elapsed_timer'):
                self.canvas_timer.delete(self.elapsed_timer)

            self.elapsed_timer = self.canvas_timer.create_text(
                10, 10,
                fill='blue',
                anchor=tk.NW,
                font=self.fontElapsed,
                text=timePrint
            )

        if updatePacing:
            if hasattr(self, 'pacing_timer'):
                self.canvas_timer.delete(self.pacing_timer)

            self.pacing_timer = self.canvas_timer.create_text(
                10, height-10,
                fill='green',
                anchor=tk.SW,
                font=self.fontPacing,
                text=timePrint
            )


    def on_destroy(self):
        self.stopFlag and self.stopFlag.set()


class TimerThread(Thread):
    def __init__(self, event, callback):
        Thread.__init__(self)

        self.stopped = event
        self.callback = callback

    def run(self):
        while not self.stopped.wait(1):
            self.callback()


def get_ideal_size(original, desired):
    ratioOrig = original[0] / original[1]
    ratioDes = desired[0] / desired[1]

    if ratioDes > ratioOrig:
        return (floor(original[0] * (desired[1] / original[1])), desired[1])
    else:
        return (desired[0], floor(original[1] * (desired[0] / original[0])))


def main(pages=None):
    root = tk.Tk()
    app = Display(root)
    root.mainloop()


if __name__ == '__main__':
    main()
