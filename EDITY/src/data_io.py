import os
import csv
import json
import yaml
from pathlib import Path
from datetime import datetime

from psychopy import gui, core

def load_config(file_name='config.yaml'):
    with open(file_name, encoding='utf_8') as yaml_file:
        config = yaml.safe_load(yaml_file)
    return config

def _monitor_file_path() -> Path:
    #zwraca ścieżkę, której używa PsychoPy do przechowywania ustawień monitorów
    base = Path(os.environ["APPDATA"])
    return base / "psychopy3" / "monitors" / "monitor.json"

def load_monitor_settings() -> dict | None:
    #Odczytuje width_cm i distance_cm z zapisanego pliku monitora

    path = _monitor_file_path()
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return {
            "width_cm":    data.get("width", None),
            "distance_cm": data.get("distance", None),
        }
    except Exception:
        return None


def run_monitor_setup() -> dict:
    #GUI do zbierania informacji i zapisywania ich
    dlg = gui.Dlg(title="Monitor setup (first-time)")
    dlg.addText(
        "No saved monitor found. Please enter your monitor's specs."
    )
    dlg.addField("Screen width (cm):",  34.0)
    dlg.addField("Viewing distance (cm):", 60.0)
    values = dlg.show()

    if not dlg.OK:
        core.quit() #użytkownik wyszedł, niespecjalnie działa bez tych informacji

    width_cm = float(values[0])
    distance_cm = float(values[1])

    #Ta część jest po to, żeby reszta była pomijana na przyszłość
    path = _monitor_file_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = {}
    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    existing["width"]    = width_cm
    existing["distance"] = distance_cm
    path.write_text(json.dumps(existing, indent=2), encoding="utf-8")

    return {"width_cm": width_cm, "distance_cm": distance_cm}


def check_monitor() -> dict:
    #To trzeba wywołać przed wszystkimi oknami PsychoPy
    #Zwraca dict: 'width_cm' i 'distance_cm'
    #Robi setup, jeśli nie ma monitora
    settings = load_monitor_settings()
    if settings is None or None in settings.values():
        settings = run_monitor_setup()
    return settings

_CSV_FIELDNAMES = [
    # Z gui
    "sub_id",
    "sub_sex",
    "sub_age",
    # metadata sesji
    "datetime",
    "block",
    "trial_num",
    # Struktura trial
    "target_shape", # Czego szuka
    "position", # Jest wyżej/niżej?
    "prime_left", # Kształt lewego
    "prime_right", # Kształt prawego
    "target_side", # Gdzie jest target?
    "target_shape_shown", # Kształt target
    "distractor_shape", # Kształt dystraktor
    "trial_type", # 'congruent' / 'incongruent' / 'neutral'
    # Odpowiedź
    "rt",
    "is_correct", # True / False
]


def _derive_trial_type(target_shape: str, prime_left: str, prime_right: str, target_side: str) -> str:
    #Jaki jest typ triala?
    if prime_left == prime_right:
        return "neutral"
    prime_on_target_side = prime_left if target_side == "left" else prime_right
    if prime_on_target_side == target_shape:
        return "congruent"
    return "incongruent"


def _ensure_csv(filepath: Path, sub_info: dict) -> bool:
    if filepath.exists():
        return False # wiemy, że istnieje, append
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_CSV_FIELDNAMES)
        writer.writeheader()
    return True


def save_trial(
    *,
    filepath: Path | str,
    sub_info: dict, #{'sub_id': ..., 'sub_sex': ..., 'sub_age': ...}
    block: int,
    trial_num: int,
    target_shape: str,
    trial_info: tuple, #(position, primes[], targetDistractor[])
    rt: float,
    is_correct: bool,
) -> None:

    #Czy trial_info jest potrzebny?
    #Ogółem do usunięcia z pól csv i tutaj to czego nie trzeba

    filepath = Path(filepath)
    _ensure_csv(filepath, sub_info)

    position_raw, primes, target_distractor = trial_info
    position_label = "up" if position_raw == 1 else "down"

    prime_left, prime_right = primes
    td_left, td_right = target_distractor

    # Po której stronie był target?
    if td_left == target_shape:
        target_side = "left"
        target_shape_shown = td_left
        distractor_shape = td_right
    else:
        target_side = "right"
        target_shape_shown = td_right
        distractor_shape = td_left

    trial_type = _derive_trial_type(
        target_shape, prime_left, prime_right, target_side
    )

    #tutaj trzeba ustalić jakie dokładnie mają być dane
    row = {
        "sub_id":            sub_info.get("sub_id", ""),
        "sub_sex":           sub_info.get("sub_sex", ""),
        "sub_age":           sub_info.get("sub_age", ""),
        "datetime":          datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "block":             block,
        "trial_num":         trial_num,
        "target_shape":      target_shape,
        "position":          position_label,
        "prime_left":        prime_left,
        "prime_right":       prime_right,
        "target_side":       target_side,
        "target_shape_shown":target_shape_shown,
        "distractor_shape":  distractor_shape,
        "trial_type":        trial_type,
        "rt":                rt,
        "is_correct":        is_correct,
    }

    with open(filepath, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_CSV_FIELDNAMES)
        writer.writerow(row)

def make_output_path(sub_id: str, data_dir: str = "data") -> Path:
    #Robi ścieżkę dla output: data/<sub_id>_<YYYYMMDD_HHMM>.csv
    #dir jest robiony jak go nie ma
    out_dir = Path(data_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    return out_dir / f"{sub_id}_{timestamp}.csv"
