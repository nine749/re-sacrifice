import pygame
from src.dependency import *
from src.battleSystem.Deck import Deck
from src.battleSystem.Vfx import Vfx
import tween

# Define the global font variable
# You can adjust the font size and type as needed
g_font = pygame.font.Font(None, 36)


class Entity:
    def __init__(self, name, animation_list, x, y, vfxAnimation_list = None, health=10):
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
        self.vfx = Vfx(vfxAnimation_list, self.x, self.y)

        # Deck & Card
        self.deck = Deck()
        self.cardsOnHand = []
        self.selectedCard = None

        # Entity Stats
        self.health = health
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

    def print_buffs(self):
        for buff in self.buffs:
            buff.print()

    def move_to(self, fieldTile, field):
        if fieldTile.is_occupied():  # Check if the fieldTile is occupied
            print("fieldTile is already occupied!")
            return

        # Start walking animation
        self.ChangeAnimation("walk")

        # Determine if the target is left or right of the current position
        self.target_position, _ = fieldTile.x, fieldTile.y
        self.facing_left = self.target_position < self.x  # Face left if moving to a lower x

        self.tweening = tween.to(
            self, "x", self.target_position, 1, "linear")  # Tween x position

        # Update fieldTile and position references
        if self.fieldTile_index is not None:
            # Remove from current fieldTile
            field[self.fieldTile_index].remove_entity()

        fieldTile.place_entity(self, self.target_position)  # Place the entity in the new fieldTile
        self.fieldTile_index = fieldTile.index  # Update the fieldTile index

    def add_buffs(self, buffList):
        for buff in buffList:
            self.buffs.append(buff)
       
    def apply_buffs_to_cardsOnHand(self):
        for card in self.cardsOnHand:
            card.reset_stats()
            for buff in self.buffs:
                if buff.is_active():
                    buff.apply(card)

    def select_card(self, card):
        self.selectedCard = card
        self.selectedCard.isSelected = True

    def remove_selected_card(self):
        self.cardsOnHand.remove(self.selectedCard)
        self.selectedCard = None

    def next_turn(self):
        # draw new card
        self.cardsOnHand.append(self.deck.draw(1)[0])

        # count down buffs
        for buff in self.buffs:
            buff.next_turn()

        # remove expired buffs
        for buff in self.buffs:
            if not buff.is_active():
                self.buffs.remove(buff)

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
        self.vfx.update(dt)

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

        # Define adjustable offsets for player and enemy
        offset_x = -55 if self.name == 'player' else -185
        offset_y = -20 if self.name == 'player' else -185

        # Update animation frame
        if self.animation_list and self.curr_animation in self.animation_list:
            # Retrieve frames from the animation object
            animation = self.animation_list[self.curr_animation]
            animation_frames = animation.get_frames()

            if animation_frames:
                # Update frame index based on the timer
                self.frame_timer += 0.01  # Increase by seconds elapsed
                if self.frame_timer >= self.frame_duration:
                    self.frame_timer = 0
                    self.frame_index = (
                        self.frame_index + 1) % len(animation_frames)

                # Render current animation frame with offsets applied
                current_frame = animation_frames[self.frame_index]
                screen.blit(
                    pygame.transform.flip(
                        current_frame, self.facing_left, False),
                    (entity_x + offset_x, entity_y + offset_y)
                )

        # Render Buff Icons
        for index, buff in enumerate(self.buffs):
            buff.x = entity_x + index * 20
            buff.render(screen)

    def ChangeAnimation(self, name):
        if name in self.animation_list:
            self.curr_animation = name
            self.frame_index = 0
            self.frame_timer = 0
            # Start from the beginning of the new animation
            self.animation_list[name].Refresh()
            print(f'{self.name} animation changed to {name}')
        else:
            print(
                f'Animation {name} not found in animation list for {self.name}')
