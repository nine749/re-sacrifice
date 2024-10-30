import pygame
from src.dependency import *
from src.resources import *


class BuffConf():
    def __init__(self, name, duration, value, sprite_collection, image=None):
        self.name = name
        self.duration = duration
        self.image = image
        self.value = value  # [1,0,0,0] == [atk,def,spd,range]
        self.sprite_collection = sprite_collection

class Buff():
    def __init__(self, conf):
        self.name = conf.name
        self.duration = conf.duration
        self.value = conf.value # [1,0,0,0] == [atk,def,spd,range]
        self.image = conf.image

        self.x = 0
        self.y = 0
        self.rect = pygame.Rect(self.x, self.y, 20, 20)

        self.tooltipFlag = False

        self.sprite_collection = conf.sprite_collection

    def print(self):
        print(f'{self.name}: {self.value} / {self.duration}')

    def apply(self, card):
        card.buffed_attack += self.value[0]
        card.buffed_defense += self.value[1]
        card.buffed_speed += self.value[2]
        card.buffed_range_end += self.value[3]

    def is_active(self):
        if self.duration == -1:  # -1 means infinite duration
            return True
        elif self.duration > 0:
            return True
        else:
            return False

    def next_turn(self):
        if self.duration > 0:
            self.duration -= 1

    def update(self, dt, events):
        self.rect.x = self.x
        self.rect.y = self.y

        mouse_pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(mouse_pos):
            self.tooltipFlag = True
        else:
            self.tooltipFlag = False

    def render(self, screen):
        if self.image is not None:
            self.y = 100
            screen.blit(self.image, (self.x, 100))

            # Determine if the buff is positive or negative
            is_positive = any(v > 0 for v in self.value)
            is_negative = any(v < 0 for v in self.value)

            # Render buff or debuff icon border
            if is_positive:
                screen.blit(self.sprite_collection['buff_icon'], (self.x, 110))
                pass
            elif is_negative:
                # Red border for negative buff
                pygame.draw.rect(screen, (255, 0, 0), (self.x,
                                 self.y, self.rect.width, self.rect.height), 1)

            # try to render buff icon border
            # pygame.draw.rect(screen, (0, 0, 0), (buff_x_position, buff.y, buff.rect.width, buff.rect.height), 1)

        if self.tooltipFlag:
            font = pygame.font.Font(None, 24)
            tooltip_text = f"{self.name}: {self.value}"
            text_surface = font.render(tooltip_text, True, (0, 0, 0))
            text_rect = text_surface.get_rect()
            text_rect.topleft = (self.rect.x + 25, self.rect.y)
            screen.blit(text_surface, text_rect)
