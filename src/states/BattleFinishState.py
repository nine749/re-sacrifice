from src.states.BaseState import BaseState
from src.dependency import *
from src.constants import *
from src.Render import *
import pygame
import sys

class BattleFinishState(BaseState):
    def __init__(self):
        super(BattleFinishState, self).__init__()


    def Enter(self, params):
        print("\n>>>>>> Enter BattleFinishState <<<<<<")
        self.player = params['player']
        self.enemy = params['enemy']
        self.field = params['field']
        self.turn = params['turn']
        self.currentTurnOwner = params['currentTurnOwner']  
        self.winner = params['winner']  

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
                if event.key == pygame.K_RETURN:
                    # TODO: Change to RPG 
                    pass

        # Update buff
        for buff in self.player.buffs:
            buff.update(dt, events)
        for buff in self.enemy.buffs:
            buff.update(dt, events)
            
        self.player.update(dt)
        self.enemy.update(dt)

    def render(self, screen):
        RenderTurn(screen, 'End State', self.turn, self.currentTurnOwner)
        RenderEntityStats(screen, self.player, self.enemy)

        text = "Player wins!" if self.winner == PlayerType.PLAYER else "Enemy wins!"
        text_surface = pygame.font.Font(None, 72).render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, (SCREEN_HEIGHT - HUD_HEIGHT)//2))

        # Draw the brown rectangle behind the text (with some padding)
        padding = 10
        pygame.draw.rect(screen, (139, 69, 19), (text_rect.x - padding, text_rect.y - padding,
                                                text_rect.width + 2 * padding, text_rect.height + 2 * padding))

        # Blit the text surface on top of the rectangle
        screen.blit(text_surface, text_rect)