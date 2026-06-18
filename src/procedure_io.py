import csv
import yaml
from pathlib import Path
from datetime import datetime

def load_config(file_name='config.yaml'):
    with open(file_name, encoding='utf_8') as yaml_file:
        config = yaml.safe_load(yaml_file)
    return config

def make_output_path(sub_id: str, data_dir: str = "data") -> Path:
    # Zrobi też folder data jak go nie ma
    out_dir = Path(data_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    return out_dir / f"{sub_id}_{timestamp}.csv"

def save_trial(filepath, sub_info, trial_num, target_shape, trial_info, rt, is_correct):
    #Dopisuje jeden trial do pliku (z nagłówkiem przy pierwszym wywołaniu)
    position = trial_info[0]
    primes = trial_info[1]
    target_distractor = trial_info[2]

    #Typ triala wynika z relacji prymów do pary target+dystraktor
    if primes[0] == primes[1]:
        trial_type = 'neutral'
    elif primes == target_distractor:
        trial_type = 'congruent'
    else:
        trial_type = 'incongruent'

    row = {
        'sub_id': sub_info['sub_id'],
        'sub_sex': sub_info['sub_sex'],
        'sub_age': sub_info['sub_age'],
        'trial_num': trial_num,
        'target_shape': target_shape,
        'position': 'up' if position == 1 else 'down',
        'prime_left': primes[0],
        'prime_right':  primes[1],
        'td_left': target_distractor[0],
        'td_right': target_distractor[1],
        'trial_type': trial_type,
        'rt': rt,
        'is_correct': is_correct,
    }

    filepath = Path(filepath)
    is_new = not filepath.exists()
    with open(filepath, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        if is_new:
            writer.writeheader()
        writer.writerow(row)