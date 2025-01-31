import pygame
from src.dependency import *
from src.battleSystem.Deck import Deck
from src.battleSystem.Vfx import Vfx
import tween

class Entity:
    def __init__(self, name, deckInv, animation_list, x, y, vfxAnimation_list, health=10, is_occupied_field = True, type = None):
        self.name = name
        self.fieldTile_index = None  # Keep track of which field it is on
        self.animation_list = animation_list
        self.curr_animation = "idle"  # Start with the idle animation
        self.frame_index = 0  # Frame index for animations
        self.frame_timer = 0  # Timer to manage frame rate
        self.frame_duration = 0.1  # Duration for each frame (adjust as needed)
        self.x = x  
        self.y = y

        # Vfx
        self.vfx = Vfx(vfxAnimation_list, self.x, self.y, self)
        self.is_occupied_field = is_occupied_field
        self.type = type

        # Deck & Card
        self.deck = Deck()
        self.deck.read_conf(deckInv)
        self.cardsOnHand = []
        self.selectedCard = None

        # Entity Stats
        self.health = health
        self.maxhealth = health
        self.attack = 0
        self.defense = 0
        self.speed = 0
        self.stunt = False
        self.buffs = []  # list of buff (or debuff?) apply on entity

        # Position
        self.target_position = None  # Target position for movement
        self.tweening = None  # Tween object for smooth movement
        self.facing_left = False  # True if the entity should face left

    def print_stats(self):
        print(f'{self.name} stats - HP: {self.health}, ATK: {self.attack}, DEF: {self.defense}, SPD: {self.speed}')

    def display_stats(self):
        self.attack = self.selectedCard.buffed_attack
        self.defense = self.selectedCard.buffed_defense
        self.speed = self.selectedCard.buffed_speed

    def reset_stats(self):
        self.attack = 0
        self.defense = 0
        self.speed = 0
        self.range = 0
        self.stunt = False
        self.vfx.stop()
        self.ChangeAnimation("idle")
    
    def reset_everything(self):
        self.reset_stats()
        self.health = self.maxhealth
        self.cardsOnHand = []
        self.selectedCard = None
        self.fieldTile_index = None
        self.buffs = [] 

    def print_buffs(self):
        for buff in self.buffs:
            buff.print()
    
    def null_function():
        pass

    def move_to(self, fieldTile, field, action = null_function):
        if fieldTile.is_occupied():  # Check if the fieldTile is occupied
            print("fieldTile is already occupied!")
            return

        # Start walking animation
        self.ChangeAnimation("walk")

        # Determine if the target is left or right of the current position
        self.target_position, _ = fieldTile.x, fieldTile.y
        self.facing_left = self.target_position < self.x  # Face left if moving to a lower x

        self.tweening = tween.to(
            self, "x", self.target_position, 1, "linear")# Tween x position
        self.tweening.on_complete(action)

        # Update fieldTile and position references
        if self.fieldTile_index is not None:
            # Remove from current fieldTile
            field[self.fieldTile_index].remove_entity()

        fieldTile.place_entity(self, self.target_position)  # Place the entity in the new fieldTile
        self.fieldTile_index = fieldTile.index  # Update the fieldTile index

    def add_buff(self, buff):
        self.buffs.append(buff)
        if buff.vfx_type == VFXType.DEBUFF:
            self.vfx.play("debuff_vfx")
        elif buff.vfx_type == VFXType.BUFF:
            self.vfx.play("buff_vfx")
        elif buff.vfx_type == VFXType.PhysicalHit: 
            self.vfx.play("physical_hit_vfx")
                
       
    def apply_buffs_to_cardsOnHand(self):
        for card in self.cardsOnHand:
            card.reset_stats()
            for buff in self.buffs:
                if buff.is_active():
                    buff.apply(card)

    def remove_expired_buffs(self):
        self.buffs = [buff for buff in self.buffs if buff.is_active()]

    def select_card(self, card):
        print(f'{self.name} selected card: {card.name} type {card.type} vfx {card.vfxType} animation {card.animationType}') 
        self.selectedCard = card
        self.selectedCard.isSelected = True
        if card.type == CardType.DEFENSE:
            print("defense card selected")
            self.vfx.play(card.vfxType)

    def remove_selected_card(self):
        try:
            self.deck.discard_pile.append(self.selectedCard)
            self.cardsOnHand.remove(self.selectedCard)
        except:
            for card in self.cardsOnHand:
                if card.name == "Ditto":
                    self.cardsOnHand.remove(card)
                    print("remove ditto")
                    break
        self.selectedCard = None

    def next_turn(self):
        # draw new card
        try:
            self.cardsOnHand.append(self.deck.draw(1)[0])
        except:
            self.deck.reset()
            self.cardsOnHand.append(self.deck.draw(1)[0])

        # count down & remove expired buffs
        for buff in self.buffs:
            buff.next_turn()
        self.remove_expired_buffs()

        # reset entity stats
        self.reset_stats()

    def select_position(self, index):
        self.index = index

    def update(self, dt):
        # Update the tween if it exists
        if self.tweening:
            self.tweening._update(dt)  # Tween progress

        if self.target_position == self.x:
            self.facing_left = False if self.name == "player" else True

        # Check if an animation is set and update it
        if self.curr_animation in self.animation_list:
            animation = self.animation_list[self.curr_animation]
            animation.update(dt)  # Progress the animation with delta time

            # If the animation has finished, switch to the idle animation
            if animation.is_finished() and self.curr_animation != "idle":
                self.ChangeAnimation("idle")
        
        # Update Vfx
        self.vfx.update(dt, self.x, self.y)

    def render(self, screen, x, y, color=(255, 0, 0)):
        # Use tweened x, y position if tween is in progress
        render_x, render_y = (self.x, self.y) if self.tweening else (x, y)

        # Define entity size
        entity_width, entity_height = 80, 80  # Example entity size

        # Calculate centered position within the field
        # Center horizontally
        entity_x = render_x + (FIELD_WIDTH - entity_width) // 2
        # Center vertically
        entity_y = render_y + (FIELD_HEIGHT - entity_height) // 2
        

        # Update animation frame
        if self.animation_list and self.curr_animation in self.animation_list:
            # Retrieve frames from the animation object
            animation = self.animation_list[self.curr_animation]
            animation_frames = animation.get_frames()
            offset_x = animation.offset_x
            offset_y = animation.offset_y
            self.frame_index = animation.index

            # Render current animation frame with offsets applied
            current_frame = animation_frames[self.frame_index]
            screen.blit(
                pygame.transform.flip(
                    current_frame, self.facing_left, False),
                (entity_x + offset_x, entity_y + offset_y)
            )

        # Render Vfx
        self.vfx.render(screen)

        # Render Buff Icons
        for index, buff in enumerate(self.buffs):
            buff.x = entity_x + index * 20
            buff.render(screen)

    def ChangeAnimation(self, name):
        if name in self.animation_list:
            self.curr_animation = name
            self.frame_index = 0
            self.frame_timer = 0
            # self.on_complete = on_complete
            # Start from the beginning of the new animation
            self.animation_list[name].Refresh()
            print(f'{self.name} animation changed to {name}')
        else:
            print(
                f'Animation {name} not found in animation list for {self.name}')

