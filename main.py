from psychopy import visual, core
from psychopy.hardware import keyboard
import random, numpy as np
from src.procedure_io import load_config

config = load_config()
win = visual.Window(color = config['window_color'], fullscr=False, checkTiming=False, units = 'pix')
kb = keyboard.Keyboard()

def prepare_data():
    target_shape = random.choice(('square','diamond'))
    trials = ((random.choice((-1,1)), (random.choice(('square','diamond')), random.choice(('square','diamond'))), random.choice((('square','diamond'), ('diamond', 'square')))) for i in range(360))
    return target_shape, trials

def draw_stimuli(size, position, shape):
    pos = {'left': (-config['stimuli_x_offset'], config['stimuli_y_offset']), 'right': (config['stimuli_x_offset'], config['stimuli_y_offset'])}[position]
    ori = {'square': 0, 'diamond': 45}[shape]
    out_rec = visual.Rect(win, width=size, height=size, pos=pos, fillColor=config['stimuli_color'], ori=ori)
    in_rec1 = visual.Rect(win, width=size * 0.8, height=size * 0.8, pos=pos, fillColor=config['window_color'], ori=ori)
    in_rec2 = visual.Rect(win, width=((size ** 2) / 2) ** (1 / 2), height=((size ** 2) / 2) ** (1 / 2), pos=pos, fillColor=config['window_color'], ori=ori + 45)
    out_rec.draw()
    in_rec1.draw()
    in_rec2.draw()
