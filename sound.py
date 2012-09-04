# -*- coding: utf-8 -*-
import pygame

bgm = None
rotate_sound = None
distroy_sound = None

def init_sound():
    global rotate_sound, bgm, distroy_sound

    pygame.init()

    bgm = pygame.mixer.Sound("sounds/bgm_106739__starsareforstaring__bomb.ogg")
    rotate_sound = pygame.mixer.Sound("sounds/rotate_bird.ogg")
    distroy_sound = pygame.mixer.Sound("sounds/distroy_87572__huluvu42__platzender-kopf-nachschlag.wav")

    bgm.set_volume(0.5)
    bgm.play(loops= -1).set_volume(0.5)
