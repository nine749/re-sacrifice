from src.resources import *

class BuffConf():
    def __init__(self, name, duration, value, imageName=None):
        self.name = name
        self.duration = duration
        self.value = value  # [1,0,0,0] == [atk,def,spd,range]
        self.imageName = imageName
        
DICE_ROLL_BUFF = {
    0: BuffConf('bonus_attack', 1, [1, 0, 0, 0], sprite_collection['attack_icon']),
    1: BuffConf('bonus_defense', 1, [0, 1, 0, 0], sprite_collection['defense_icon']),
    2: BuffConf('bonus_speed', 1, [0, 0, 1, 0], sprite_collection['speed_icon']),
}