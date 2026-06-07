from psychopy import visual, core, monitors
import numpy as np
import tkinter as tk

from src.data_io import check_monitor

def _get_screen_resolution() -> tuple[int, int]:
    #tkinter pozwala czytać rozdzielczość bez PsychoPy
    #No i okna z tkintera nie widać, bo jest od razu ukrywane
    root = tk.Tk()
    root.withdraw()
    w = root.winfo_screenwidth()
    h = root.winfo_screenheight()
    root.destroy()
    return w, h

def make_window(monitor_settings: dict | None = None) -> visual.Window:
    #Okno do PsychoPy
    #monitor_settings to ten dict
    #jak go nie ma, to check_monitor jest wywołany

    if monitor_settings is None:
        monitor_settings = check_monitor()

    screen_w, screen_h = _get_screen_resolution()

    mon = monitors.Monitor("monitor")
    mon.setWidth(monitor_settings["width_cm"])
    mon.setDistance(monitor_settings["distance_cm"])
    mon.setSizePix([screen_w, screen_h])

    win = visual.Window(
        monitor=mon,
        units="deg",
        color="white",
        fullscr=True,
        checkTiming=False,
    )
    return win


def dynamic_fix(win: visual.Window) -> None:
    DURATION = 0.750
    SIDE     = 19.0
    DOT_SIZE = 0.2
    offset = SIDE / 2.0

    start_pos = np.array([
        [-offset,  offset],   # top-left
        [ offset,  offset],   # top-right
        [-offset, -offset],   # bottom-left
        [ offset, -offset],   # bottom-right
    ])
    end_pos = np.zeros((4, 2))

    dots = visual.ElementArrayStim(
        win,
        nElements=4,
        elementTex=None,
        elementMask="circle",
        sizes=DOT_SIZE,
        xys=start_pos,
        colors="black",
        units="deg",
    )

    clock = core.Clock()
    clock.reset()
    t = 0.0
    while t < DURATION:
        t = clock.getTime()
        frac = min(t / DURATION, 1.0)
        dots.xys = start_pos + (end_pos - start_pos) * frac
        dots.draw()
        win.flip()

    win.flip() #pusta klatka