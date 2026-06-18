from psychopy import visual, core, monitors, gui
import tkinter as tk
import json
import os
from pathlib import Path

def _get_screen_resolution():
    #tkinter pomaga z czytaniem rozdzielczości
    root = tk.Tk()
    root.withdraw()
    w = root.winfo_screenwidth()
    h = root.winfo_screenheight()
    root.destroy()
    return w, h

def make_window(monitor_settings: None, color: str = "white"):
    if monitor_settings is None:
        monitor_settings = check_monitor()

    screen_w, screen_h = _get_screen_resolution()

    #PsychoPy ma tendencję się psuć, jak używa się jego setterów, nie ruszać
    mon = monitors.Monitor(name="monitor")
    mon.currentCalib = {
        'width': monitor_settings["width_cm"],
        'distance': monitor_settings["distance_cm"],
        'sizePix': [screen_w, screen_h],
    }

    win = visual.Window(
        size=[screen_w, screen_h],
        monitor=mon,
        units="deg",
        color=color,
        fullscr=True,
        checkTiming=False,
    )
    return win

def _monitor_file_path():
    #JSON projektu, wywalony z psychopy3/monitors, żeby nie próbował go czytać.
    #Centrum monitorów jest nieposłuszne
    base = Path(os.environ["APPDATA"])
    return base / "psychopy3" / "monitor.json"

def load_monitor_settings():

    path = _monitor_file_path()
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return {
            "width_cm":    data.get("width_cm"),
            "distance_cm": data.get("distance_cm"),
        }
    except Exception:
        return None

def run_monitor_setup():
    #Setup pierwszego uruchomienia; quit jak anulowane
    dlg = gui.Dlg(title="Monitor setup (first-time)")
    dlg.addText("No monitor found. Please enter your monitor's specs.")
    dlg.addField("Screen width (cm):", 34.0)
    dlg.addField("Viewing distance (cm):", 60.0)
    values = dlg.show()
    if not dlg.OK:
        core.quit()

    settings = {"width_cm": float(values[0]), "distance_cm": float(values[1])}

    #Trzyma dla kolejnej sesji
    path = _monitor_file_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(settings, indent=2), encoding="utf-8")
    return settings

def save_monitor_settings(settings: dict):
    #Nadpisuje plik monitora
    path = _monitor_file_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(settings, indent=2), encoding="utf-8")

def check_monitor():
    #Przed oknem PsychoPy
    #Odpala setup jak ich nie ma
    settings = load_monitor_settings()
    if settings is None or None in settings.values():
        settings = run_monitor_setup()
    return settings