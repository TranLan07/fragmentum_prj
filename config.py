import pygame
import os
from dataclasses import dataclass

f = open('config.txt', 'r')
config = f.readlines()
f.close()

for i in range(len(config)):
    config[i] = config[i].strip()

# Extraction des données de configuration
def extract_data_line(dt_name):
    for i in range(len(config)):
        scr = config[i].split('#')
        if scr[0] == dt_name:
            return scr
    return None

scr_e = extract_data_line('screen_resolution')
def screen_re():
    global scr_e
    scr = scr_e
    if scr != None:
        try:
            scr = (int(scr[1]), int(scr[2]))
        except:
            return (800, 800)
    else:
        return (800, 800)
    return scr

def fps_re():
    scr = extract_data_line('fps')
    if scr != None:
        try:
            scr = int(scr[1])
        except:
            return 120
    else:
        return 120
    return scr

def delta_t_re():
    return 1/fps_re()

# Mapping des touches - a été adapté pour le clavier AZERTY français
keybinds = {
    'a': pygame.K_a,
    'b': pygame.K_b,
    'c': pygame.K_c,
    'd': pygame.K_d,
    'e': pygame.K_e,
    'f': pygame.K_f,
    'g': pygame.K_g,
    'h': pygame.K_h,
    'i': pygame.K_i,
    'j': pygame.K_j,
    'k': pygame.K_k,
    'l': pygame.K_l,
    'm': pygame.K_m,
    'n': pygame.K_n,
    'o': pygame.K_o,
    'p': pygame.K_p,
    'q': pygame.K_q,
    'r': pygame.K_r,
    's': pygame.K_s,
    't': pygame.K_t,
    'u': pygame.K_u,
    'v': pygame.K_v,
    'w': pygame.K_w,
    'x': pygame.K_x,
    'y': pygame.K_y,
    'z': pygame.K_z,
    ' ': pygame.K_SPACE,
    'ctrl': pygame.K_LCTRL,
    'shift': pygame.K_LSHIFT,
    'alt': pygame.K_LALT
}

# Configuration des touches par défaut
Jump = ' '
Forward = 'd'
Backward = 'q'
Save = 's'
Boost = 'shift'
Double_jump = 'e'

def jump_key():
    return keybinds[Jump]

def Save_key():
    return keybinds[Save]

def forward_key():
    return keybinds[Forward]

def backward_key():
    return keybinds[Backward]

def boost_key():
    return keybinds[Boost]

def double_jump_key():
    return keybinds[Double_jump]

# Musique
def get_music_files():
    """Renvoie la liste des fichiers musicaux"""
    music_list = []
    music_dir = "assets/sound"
    if os.path.exists(music_dir):
        for file in os.listdir(music_dir):
            if file.endswith(('.mp3', '.wav', '.ogg', '.crdownload')):
                music_list.append(os.path.join(music_dir, file))
    else:
        music_list = ["assets/sound/SDM - BOLIDE ALLEMAND.mp3"]

    return music_list