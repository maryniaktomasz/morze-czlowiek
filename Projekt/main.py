from psychopy import visual, gui, core
from psychopy.hardware import keyboard
import random
import numpy as np
from src.procedure_io import make_output_path, save_trial, load_config
from src.monitor import make_window, check_monitor, save_monitor_settings

config = load_config()

# losuje kształt docelowy i listę danych do pojedyńczych triali (wyświetlenie bodźca góra/dół, (lewy bodziec, prawy bodziec),  (lewy bodziec, prawy bodziec))
def prepare_data():
    target_shape = random.choice(('square', 'diamond'))
    trials = list(
        (
            random.choice((-1, 1)),
            (random.choice(('square', 'diamond')), random.choice(('square', 'diamond'))),
            random.choice((('square', 'diamond'), ('diamond', 'square')))
        )
        for i in range(config['number_of_trials_per_block']*config['number_of_blocks'])
    )
    return target_shape, trials

# rysuje i wyświetla dynamic fix
def dynamic_fix(win: visual.Window):

    offset = config['dynamic_fix_side'] / 2.0

    start_pos = np.array([
        [-offset,  offset], # top-left
        [ offset,  offset], # top-right
        [-offset, -offset], # bottom-left
        [ offset, -offset], # bottom-right
    ])
    end_pos = np.zeros((4, 2))

    dots = visual.ElementArrayStim(
        win,
        nElements=4,
        elementTex=None,
        elementMask="circle",
        sizes=config['dynamic_fix_dot_size'],
        xys=start_pos,
        colors=config['stimuli_color'],
        units="deg",
    )

    clock = core.Clock()
    clock.reset()
    t = 0.0
    # fr_det kompensuje opóźnienie vsync win.flip(), ostatnia klatka ląduje na duration
    while t < config['dynamic_fix_duration'] - fr_det:
        t = clock.getTime()
        # postęp animacji 0-1, 1.0 chroni przed przeskokiem jak t przekroczy duration
        frac = min(t / config['dynamic_fix_duration'], 1.0)
        dots.xys = start_pos + (end_pos - start_pos) * frac
        dots.draw()
        win.flip()

    win.flip()

# rysuje bodziec o rozmiarze size, po stronie position_x ['left'/'right'/'center'], na górze bądź dole position_y [1/-1], o kształcie shapie ['square'/'diamond']
def draw_stimuli(size, position_x, position_y, shape):
    pos = {
        'left': (-config['stimuli_x_offset'], config['stimuli_y_offset'] * position_y),
        'right': ( config['stimuli_x_offset'], config['stimuli_y_offset'] * position_y),
        'center': ( 0, config['stimuli_y_offset'] * position_y)
    }[position_x]
    ori = {'square': 0, 'diamond': 45}[shape]
    out_rec = visual.Rect(win, width=size, height=size, pos=pos, fillColor=config['stimuli_color'], ori=ori)
    in_rec1 = visual.Rect(win, width=size *config['stimuli_thicknes'], height=size *config['stimuli_thicknes'], pos=pos, fillColor=config['window_color'], ori=ori)
    in_rec2 = visual.Rect(win, width=((size**2)/2)**(1/2), height=((size**2)/2)**(1/2), pos=pos, fillColor=config['window_color'], ori=ori + 45)
    out_rec.draw(); in_rec1.draw(); in_rec2.draw()

# przeprowadza pojedyńczą próbę dla kształtu docelowego target ['square'/'diamond'], o danych z trail_info (jak z prepere_data()) i nie wyświetla prymów gdy is_training jest True
def trial(target, trial_info, is_training=False):
    dynamic_fix(win)
    if not is_training:
        draw_stimuli(config['stimuli_size'] *config['stimuli_thicknes'], 'left',  trial_info[0], trial_info[1][0])
        draw_stimuli(config['stimuli_size'] *config['stimuli_thicknes'], 'right', trial_info[0], trial_info[1][1])
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
    kb.waitKeys(maxWait=config['target_time'] - fr_det, keyList=(config['left_key'], config['right_key'], config['quit_key']), clear=False)
    win.flip()
    kb.waitKeys(keyList=(config['left_key'], config['right_key'],config['quit_key']), clear=False)
    pressed = kb.getKeys()
    if pressed[-1] == config['quit_key']: #wyjście z eksperymentu w trakcie trwania
        kb.getKeys()
        for i in range(5, -1, -1):
            text = visual.TextStim(win, text=f'Naciśnij ponownie {config["quit_key"].upper()} w ciągu {i} sekund aby opuścić procedurę.', color=config['stimuli_color'],
                                   height=config['stimuli_size'] * 0.5, font=config['text_font'])
            text.draw()
            win.flip()
            kb.waitKeys(maxWait= 1, keyList=(config['quit_key']), clear=False)
            pressed2 = kb.getKeys()
            if len(pressed2) > 0 and pressed2[-1] == config['quit_key']:
                win.close()
                core.quit()
        text = visual.TextStim(win,text=f'Naciśnij {config["left_key"].upper()} lub {config["right_key"].upper()} aby kontynuować.',color=config['stimuli_color'],height=config['stimuli_size'] * 0.5, font=config['text_font'])
        text.draw()
        win.flip()
        kb.waitKeys(keyList=(config['left_key'], config['right_key']), clear=False)
        pressed = kb.getKeys()
    if trial_info[2][{config['left_key']: 0, config['right_key']: 1}[pressed[-1].value]] == target:
        return True, pressed[-1].rt
    else:
        return False, pressed[-1].rt

# przeprowadza ćwiczenia dla kształtu docelowego target
def run_exercise(target):
    info = visual.TextStim(win, text='', color=config['stimuli_color'], height=config['stimuli_size']*1.5, font=config['text_font'])

    for exercise in range(config['number_of_exercises']):
        is_correct, _ = trial(target, (random.choice((-1,1)), (random.choice(('square','diamond')), random.choice(('square','diamond'))), random.choice((('square','diamond'), ('diamond', 'square')))), True)
        info.setText({True: 'Dobrze', False: 'Źle'}[is_correct])
        info.draw()
        win.callOnFlip(kb.clearEvents)
        win.callOnFlip(kb.clock.reset)
        win.flip()
        while kb.clock.getTime() < config['between_trial_time'] - fr_det:
            continue

# --------- Eksperyment ---------

monitor_settings = check_monitor()

# robi gui z informacjami o osobie badanej i monitorze
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

new_width = float(gui_data[3])
new_distance = float(gui_data[4])
if new_width != monitor_settings['width_cm'] or new_distance != monitor_settings['distance_cm']:
    monitor_settings = {'width_cm': new_width, 'distance_cm': new_distance}
    save_monitor_settings(monitor_settings)

csv_path = make_output_path(sub_info['sub_id'])

win = make_window(monitor_settings, color=config['window_color'])
kb = keyboard.Keyboard()

# wyliczenie czasu jednej klatki
win.callOnFlip(kb.clearEvents)
win.callOnFlip(kb.clock.reset)
win.flip()
win.flip()
fr_det = kb.clock.getTime()

# losowanie danych
target_shape, trials = prepare_data()

# instrukacja
file_path = 'instruction.txt'
with open(file_path, 'r', encoding='utf-8') as file:
    instruction = file.read()

text = visual.TextStim(win, text = instruction + '\nNaciśnij SPACJĘ, aby poznać swoją figurę.', color=config['stimuli_color'], height=config['stimuli_size'] * 0.5, font=config['text_font'])
text.draw()
win.flip()
kb.waitKeys(keyList='space', clear=True)
text = visual.TextStim(win, text='Twoją figurą docelową jest:', color=config['stimuli_color'], height=config['stimuli_size'] * 0.5, font=config['text_font'])
text.draw()
draw_stimuli(config['stimuli_size'], 'center', -1, target_shape)
win.flip()
kb.waitKeys(keyList='space', clear=True)

# ćwiczenie
text = visual.TextStim(win, text='Naciśnij SPACJĘ, aby rozpocząć ćwiczenie.', color=config['stimuli_color'], height=config['stimuli_size'] * 0.5, font=config['text_font'])
text.draw()
win.flip()
kb.waitKeys(keyList='space', clear=True)
run_exercise(target_shape)
text = visual.TextStim(win, text='Ćwiczenie zakończone.\nNaciśnij SPACJĘ, aby rozpocząć właściwe badanie.', color=config['stimuli_color'], height=config['stimuli_size'] * 0.5, font=config['text_font'])
text.draw()
win.flip()
kb.waitKeys(keyList='space', clear=True)

# badanie właściwe
for j in range(config['number_of_blocks']):
    for i, t_info in enumerate(trials[j*config['number_of_trials_per_block']:(j+1)*config['number_of_trials_per_block']]):
        is_correct, rt = trial(target_shape, t_info)
        save_trial(csv_path, sub_info, j*config['number_of_trials_per_block'] + i, target_shape, t_info, rt, is_correct)

    if j + 1 < config['number_of_blocks']:
        text = visual.TextStim(win, text='Możesz teraz odpocząć.\nNaciśnij SPACJĘ, aby kontynuować.', color=config['stimuli_color'], height=config['stimuli_size'] * 0.5, font=config['text_font'])
        text.draw()
        win.flip()
        kb.waitKeys(keyList='space', clear=True)

text = visual.TextStim(win, text='To koniec badania.\nNaciśnij SPACJĘ, aby zakończyć.', color=config['stimuli_color'], height=config['stimuli_size'] * 0.5, font=config['text_font'])
text.draw()
win.flip()
kb.waitKeys(keyList='space', clear=True)

win.close()
core.quit()
