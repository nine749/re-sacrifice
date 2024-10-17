from src.dependency import *
from src.constants import *
from src.cardSystem.FieldTile import FieldTile
from src.cardSystem.Buff import Buff
import pygame
import sys
import random

class BattleInitialState(BaseState):
    def __init__(self):
        super(BattleInitialState, self).__init__()
        self.cards = []
        self.entities = []
        self.dice = 0
        self.roll = False

        # Create field
        self.field = self.create_field(9)  # Create 9 field in a single row

    def Enter(self, params):
        print(">>>>>> Enter BattleInitialState <<<<<<")

        self.deck = params['deck']
        self.player = params['player']
        self.enemy = params['enemy']
        self.turn = params['turn']
        self.currentTurnOwner = params['currentTurnOwner']  
        self.nextTurn()

        # Mock move entities
        self.player.move_to(self.field[0], self.field)
        self.enemy.move_to(self.field[8], self.field)
        for fieldTile in self.field:
            print(f'FieldTile {fieldTile.index} is occupied by {fieldTile.entity.name if fieldTile.entity else None}')

        for card in self.player.cardsOnHand:
            print("Player's Hand Card: ", card.name)

    def nextTurn(self):
        # Change turn owner
        if self.currentTurnOwner == PlayerType.PLAYER:
            self.currentTurnOwner = PlayerType.ENEMY
        else:
            self.currentTurnOwner = PlayerType.PLAYER

        # Increment turn
        self.turn += 1

    def Exit(self):
        pass

    def update(self, dt, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_SPACE and self.roll == False:
                    self.roll_dice()
                    self.roll = True
                elif event.key == pygame.K_RETURN and self.roll == True:
                    g_state_manager.Change(BattleState.SELECTION_PHASE, {
                        'player': self.player,
                        'enemy': self.enemy,
                        'field': self.field,
                        'turn': self.turn,
                        'currentTurnOwner': self.currentTurnOwner
                    })

    def render(self, screen):
        # Title
        if self.roll:
            screen.blit(pygame.font.Font(None, 36).render("Cards:    Press Enter start", True, (255, 255, 255)), (10, SCREEN_HEIGHT - HUD_HEIGHT + 10))   
        else:
            screen.blit(pygame.font.Font(None, 36).render("Cards:    Press Spacebar to Roll the dice", True, (255, 255, 255)), (10, SCREEN_HEIGHT - HUD_HEIGHT + 10))   
        
        # Render cards on player's hand
        for order, card in enumerate(self.player.cardsOnHand):
            card.render(screen, order)

        # Render field
        for fieldTile in self.field:
            fieldTile.render(screen, len(self.field))

        # Clear only the dice result area (fill the area with the background color)
        pygame.draw.rect(screen, (255, 255, 255), (10, SCREEN_HEIGHT - HUD_HEIGHT - 40, 150, 40))  # Adjust size and position based on your layout

        # Render dice result
        screen.blit(pygame.font.Font(None, 36).render("Dice: " + str(self.dice), True, (0, 0, 0)), (10, SCREEN_HEIGHT - HUD_HEIGHT - 30))

    def create_field(self, num_fieldTile):
        field = []
        for i in range(num_fieldTile):
            x = i * 100  # Adjust the x position based on index
            y = 200  # Since you have only one row, y is constant
            field.append(FieldTile(i, (x, y)))  # Create and append each fieldTile
        return field
    
    def roll_dice(self):
        # Play dice sound
        dice_sound = pygame.mixer.Sound("sounds/dice_roll.mp3")
        dice_sound.play()

        # Render dice rolling animation
        for _ in range(30):  # Increase the number of iterations for a smoother effect
            self.dice = random.randint(1, 6)  # Randomly change the dice number
            self.render(pygame.display.get_surface())  # Render the current state of the screen
            pygame.display.flip()  # Update the display to show changes
            pygame.time.delay(10)  # Delay to control the speed of dice rolling

        # Roll the dice and convert the value to buff
        final_number = random.randint(1, 6)
        self.dice_buff(final_number)

    def dice_buff(self, diceNumber):
        if diceNumber <= 4:               # 1, 2, 3, 4
            value = [0, 0, 0, 0]    # atk, def, spd, range
            value[diceNumber-1] = 1
            buff = Buff("bonus", 1, value)
            if self.currentTurnOwner == PlayerType.PLAYER:   
                self.player.add_buff(buff)
            elif self.currentTurnOwner == PlayerType.ENEMY:
                self.enemy.add_buff(buff)
        else:
            print('no buff')