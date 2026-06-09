from psychopy import visual, gui, core
from psychopy.hardware import keyboard
import random
from src.data_io import check_monitor, save_monitor_settings, make_output_path, save_trial, load_config
from src.Fix import make_window, dynamic_fix

config = load_config()

def prepare_data():
    target_shape = random.choice(('square', 'diamond'))
    trials = list(
        (
            random.choice((-1, 1)),
            (random.choice(('square', 'diamond')), random.choice(('square', 'diamond'))),
            random.choice((('square', 'diamond'), ('diamond', 'square')))
        )
        for i in range(20)
    )
    return target_shape, trials

def draw_stimuli(size, position_x, position_y, shape):
    pos = {
        'left':  (-config['stimuli_x_offset'], config['stimuli_y_offset'] * position_y),
        'right': ( config['stimuli_x_offset'], config['stimuli_y_offset'] * position_y),
    }[position_x]
    ori = {'square': 0, 'diamond': 45}[shape]
    out_rec  = visual.Rect(win, width=size,           height=size,           pos=pos, fillColor=config['stimuli_color'], ori=ori)
    in_rec1  = visual.Rect(win, width=size * 0.8,     height=size * 0.8,     pos=pos, fillColor=config['window_color'],  ori=ori)
    in_rec2  = visual.Rect(win, width=((size**2)/2)**(1/2), height=((size**2)/2)**(1/2),
                           pos=pos, fillColor=config['window_color'], ori=ori + 45)
    out_rec.draw(); in_rec1.draw(); in_rec2.draw()

def trial(target, trial_info, is_training=False):
    dynamic_fix(win)
    if not is_training:
        draw_stimuli(config['stimuli_size'] * 0.8, 'left',  trial_info[0], trial_info[1][0])
        draw_stimuli(config['stimuli_size'] * 0.8, 'right', trial_info[0], trial_info[1][1])
        win.callOnFlip(kb.clearEvents)
        win.callOnFlip(kb.clock.reset)
        win.flip()
        while kb.clock.getTime() < config['prime_time'] - fr_det:
            continue
        win.callOnFlip(kb.clearEvents)
        win.callOnFlip(kb.clock.reset)
        win.flip()
    draw_stimuli(config['stimuli_size'], 'left',  trial_info[0], trial_info[2][0])
    draw_stimuli(config['stimuli_size'], 'right', trial_info[0], trial_info[2][1])
    while kb.clock.getTime() < config['isi_time'] - fr_det:
        continue
    win.callOnFlip(kb.clearEvents)
    win.callOnFlip(kb.clock.reset)
    win.flip()
    kb.waitKeys(maxWait=config['target_time'] - fr_det,
                keyList=(config['left_key'], config['right_key']), clear=False)
    win.flip()
    kb.waitKeys(keyList=(config['left_key'], config['right_key']), clear=False)
    pressed = kb.getKeys()
    if trial_info[2][{config['left_key']: 0, config['right_key']: 1}[pressed[-1].value]] == target:
        return True, pressed[-1].rt
    else:
        return False, pressed[-1].rt

def run_exercise(target):
    info = visual.TextStim(win, text='', color=config['stimuli_color'], height=config['stimuli_size']*3)

    for exercise in range(config['number_of_exercises']):
        is_correct, _x = trial(target, (random.choice((-1,1)), (random.choice(('square','diamond')), random.choice(('square','diamond'))), random.choice((('square','diamond'), ('diamond', 'square')))), True)
        info.setText({True: 'Dobrze', False: 'Źle'}[is_correct])
        info.draw()
        win.callOnFlip(kb.clearEvents)
        win.callOnFlip(kb.clock.reset)
        win.flip()
        while kb.clock.getTime() < config['between_trial_time'] - fr_det:
            continue

monitor_settings = check_monitor()

myDlg = gui.Dlg(title='')
myDlg.addText('Subject info:')
myDlg.addField('sub_id',  '')
myDlg.addField('sub_sex', choices=['Male', 'Female', 'Other'])
myDlg.addField('sub_age', 20)
myDlg.addText('Monitor (confirm or adjust):')
myDlg.addField('Screen width (cm):',     monitor_settings['width_cm'])
myDlg.addField('Viewing distance (cm):', monitor_settings['distance_cm'])
gui_data = myDlg.show()
if not myDlg.OK:
    core.quit()

sub_info = {
    'sub_id':  gui_data[0],
    'sub_sex': gui_data[1],
    'sub_age': gui_data[2],
}

new_width    = float(gui_data[3])
new_distance = float(gui_data[4])
if new_width != monitor_settings['width_cm'] or new_distance != monitor_settings['distance_cm']:
    monitor_settings = {'width_cm': new_width, 'distance_cm': new_distance}
    save_monitor_settings(monitor_settings)

csv_path = make_output_path(sub_info['sub_id'])

win = make_window(monitor_settings, color=config['window_color'])
kb = keyboard.Keyboard()
win.callOnFlip(kb.clearEvents)
win.callOnFlip(kb.clock.reset)
win.flip()
win.flip()
fr_det = kb.clock.getTime()

target_shape, trials = prepare_data()
run_exercise(target_shape)
for i, t_info in enumerate(trials):
    is_correct, rt = trial(target_shape, t_info)
    save_trial(csv_path, sub_info, i, target_shape, t_info, rt, is_correct)

win.close()
core.quit()