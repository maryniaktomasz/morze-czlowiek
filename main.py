from psychopy import visual, core
from psychopy.hardware import keyboard
import random, numpy as np
from src.procedure_io import load_config

config = load_config()
win = visual.Window(color = config['window_color'], fullscr=False, checkTiming=False, units='pix')
kb = keyboard.Keyboard()

win.callOnFlip(kb.clearEvents)
win.callOnFlip(kb.clock.reset)
win.flip()
win.flip()
fr_det = kb.device.clock.getTime()

def prepare_data():
    target_shape = random.choice(('square','diamond'))
    trials = list((random.choice((-1,1)), (random.choice(('square','diamond')), random.choice(('square','diamond'))), random.choice((('square','diamond'), ('diamond', 'square')))) for i in range(360))
    return target_shape, trials

def draw_stimuli(size, position_x, position_y, shape):
    pos = {'left': (-config['stimuli_x_offset'], config['stimuli_y_offset']*position_y), 'right': (config['stimuli_x_offset'], config['stimuli_y_offset']*position_y)}[position_x]
    ori = {'square': 0, 'diamond': 45}[shape]
    out_rec = visual.Rect(win, width=size, height=size, pos=pos, fillColor=config['stimuli_color'], ori=ori)
    in_rec1 = visual.Rect(win, width=size * 0.8, height=size * 0.8, pos=pos, fillColor=config['window_color'], ori=ori)
    in_rec2 = visual.Rect(win, width=((size ** 2) / 2) ** (1 / 2), height=((size ** 2) / 2) ** (1 / 2), pos=pos, fillColor=config['window_color'], ori=ori + 45)
    out_rec.draw()
    in_rec1.draw()
    in_rec2.draw()

def trial(target, trial_info, is_training = False):
        # dynamic_fix()
        if not is_training:
            draw_stimuli(config['stimuli_size']*0.8,'left', trial_info[0], trial_info[1][0])
            draw_stimuli(config['stimuli_size']*0.8,'right', trial_info[0], trial_info[1][1])
            win.callOnFlip(kb.clearEvents)
            win.callOnFlip(kb.clock.reset)
            win.flip()
            while kb.device.clock.getTime() < config['prime_time'] - fr_det:
                continue
            win.callOnFlip(kb.clearEvents)
            win.callOnFlip(kb.clock.reset)
            win.flip()
        draw_stimuli(config['stimuli_size'], 'left', trial_info[0], trial_info[2][0])
        draw_stimuli(config['stimuli_size'], 'right', trial_info[0], trial_info[2][1])
        while kb.device.clock.getTime() < config['isi_time'] - fr_det:
            continue
        win.callOnFlip(kb.clearEvents)
        win.callOnFlip(kb.clock.reset)
        win.flip()
        kb.waitKeys(maxWait= config['target_time'] - fr_det, keyList= (config['left_key'],config['right_key']), clear=False)
        win.flip()
        kb.waitKeys(keyList= (config['left_key'],config['right_key']), clear=False)
        pressed = kb.getKeys()
        if trial_info[2][{config['left_key']: 0, config['right_key']: 1}[pressed[-1].value]] == target:
            return True, pressed[-1].rt
        else:
            return False, pressed[-1].rt
