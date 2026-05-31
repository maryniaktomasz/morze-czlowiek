from psychopy import visual, core, monitors
import numpy as np

SCREEN_WIDTH_CM = 34.0
VIEW_DISTANCE_CM = 60.0

def make_window():
    mon = monitors.Monitor('monitor')   # trzeba mieć w %APPDATA%/psychopy3/monitors plik monitor.json
    win = visual.Window(
        monitor=mon,
        units='deg',
        color='white',
        fullscr=True
    )
    return win

def dynamic_fix():
    DURATION = 0.750          # 750 ms
    SIDE = 19.0               # bok kwadratu utworzonego przez kropki (deg)
    DOT_SIZE = 0.2            # rozmiar kropki (deg)

    offset = SIDE / 2.0       # żeby każdą kropkę przesunąć o ten sam dystans w każdą stronę

    start_pos = np.array([
        [-offset,  offset],   # lewy górny
        [ offset,  offset],   # prawy górny
        [-offset, -offset],   # lewy dolny
        [ offset, -offset],   # prawy dolny
    ])
    end_pos = np.zeros((4, 2))

    dots = visual.ElementArrayStim(
        win,
        nElements=4,
        elementTex=None,
        elementMask='circle',
        sizes=DOT_SIZE,
        xys=start_pos,
        colors='black',
        units='deg',
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

    win.flip()


if __name__ == '__main__':
    win = make_window()
    dynamic_fix()
    win.close()
    core.quit()