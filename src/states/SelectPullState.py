from src.states.BaseState import BaseState
from src.dependency import *
from src.constants import *
from src.Render import *
import pygame
import sys

class SelectPullState(BaseState):
    def __init__(self):
        super(SelectPullState, self).__init__()

    def Enter(self, params):
        self.params = params
        battle_param = self.params['battleSystem']
        self.player = battle_param['player']
        self.enemy = battle_param['enemy']
        self.field = battle_param['field']
        self.turn = battle_param['turn']
        self.currentTurnOwner = battle_param['currentTurnOwner']  
        self.effectOrder = battle_param['effectOrder']
        self.effect = battle_param['effect']
        self.effectOwner = battle_param['effectOwner']

        self.availablePullTile = []

        if self.effectOwner == PlayerType.PLAYER:
            if self.player.fieldTile_index > self.enemy.fieldTile_index:
                self.MinTileIndex = self.enemy.fieldTile_index + self.effect.minRange
                self.MaxTileIndex = self.enemy.fieldTile_index + self.effect.maxRange
            else:
                self.MinTileIndex = self.enemy.fieldTile_index - self.effect.minRange
                self.MaxTileIndex = self.enemy.fieldTile_index - self.effect.maxRange 
        elif self.effectOwner == PlayerType.ENEMY: 
            if self.enemy.fieldTile_index > self.player.fieldTile_index:
                self.MinTileIndex = self.player.fieldTile_index + self.effect.minRange
                self.MaxTileIndex = self.player.fieldTile_index + self.effect.maxRange
            else:
                self.MinTileIndex = self.player.fieldTile_index - self.effect.minRange
                self.MaxTileIndex = self.player.fieldTile_index - self.effect.maxRange       


        if self.MaxTileIndex < 0:
            self.MaxTileIndex = 0
        elif self.MaxTileIndex > 8:
            self.MaxTileIndex = 8
        
        self.selectPullTile = 0
        if self.MaxTileIndex <= self.MinTileIndex:
            for i in range(self.MaxTileIndex, self.MinTileIndex+1):
                self.availablePullTile.append(i)
        else:       
            for j in range(self.MinTileIndex, self.MaxTileIndex+1):
                self.availablePullTile.append(j)
        
        self.availablePullTile = list( dict.fromkeys(self.availablePullTile) )
        
        print('\n!!!! SelectPullState !!!!')
        print(f'Owner: {self.effectOwner}')
        print(f'Effect: {self.effect.type} ({self.effect.minRange} - {self.effect.maxRange})')
        print(f'SelectPullTile: {self.selectPullTile}')
        
        # apply buff to all cards on hand
        self.player.apply_buffs_to_cardsOnHand()
        self.enemy.apply_buffs_to_cardsOnHand()

        # display entity stats
        self.player.display_stats()
        self.enemy.display_stats()

        

    def Exit(self):
        pass

    def remove_timeout_entity(self):
        for tile in self.field:
            if tile.is_second_entity():
                if tile.second_entity.duration == 0:
                    print("remove second entity for timeout ", tile.index)
                    tile.remove_second_entity()

    def update(self, dt, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_SPACE:
                    pass
                if event.key == pygame.K_LEFT:
                    print('key left')
                    if self.effectOwner == PlayerType.PLAYER:
                        print('moving left')
                        self.selectPullTile = self.selectPullTile - 1
                        if self.selectPullTile < 0:
                            self.selectPullTile = len(self.availablePullTile) - 1
                if event.key == pygame.K_RIGHT:
                    print('key right')
                    if self.effectOwner == PlayerType.PLAYER:
                        print('moving right')
                        self.selectPullTile = self.selectPullTile + 1
                        if self.selectPullTile > len(self.availablePullTile) - 1:
                            self.selectPullTile = 0
                if event.key == pygame.K_RETURN:
                    print('Pull state: before check effect owner')
                    if self.effectOwner == PlayerType.PLAYER:
                        print('enemy Pull')
                        if self.selectPullTile>=0 and self.effect.maxRange>0:
                            if not self.field[self.availablePullTile[self.selectPullTile]].is_occupied():
                                self.enemy.move_to(self.field[self.availablePullTile[self.selectPullTile]], self.field)
                                print(f"Pull target to {self.availablePullTile[self.selectPullTile]}")
                            else:
                                print("can not Pull, there is an entity of that tile")
                        else:
                            print("there is no Pull happen")
                    else:
                        print("enemy Pull")
                    print('Pull state: after check effect owner')
                    if self.player.health > 0 and self.enemy.health > 0:
                        self.params['battleSystem'] = {
                            'player': self.player,
                            'enemy': self.enemy,
                            'field': self.field,
                            'turn': self.turn,
                            'currentTurnOwner': self.currentTurnOwner,
                            'effectOrder': self.effectOrder
                        }
                        g_state_manager.Change(BattleState.RESOLVE_PHASE, self.params)
                    else:
                        if self.player.health <= 0:
                            self.winner = PlayerType.ENEMY
                        elif self.enemy.health <= 0:
                            self.winner = PlayerType.PLAYER
                        self.params['battleSystem'] = {
                            'player': self.player,
                            'enemy': self.enemy,
                            'field': self.field,
                            'turn': self.turn,
                            'currentTurnOwner': self.currentTurnOwner,
                            'winner': self.winner
                        }
                        g_state_manager.Change(BattleState.FINISH_PHASE, self.params)

        for buff in self.player.buffs:
            buff.update(dt, events)
        for buff in self.enemy.buffs:
            buff.update(dt, events)

        self.player.update(dt)
        self.enemy.update(dt)

        for tile in self.field:
            if tile.second_entity:
                tile.second_entity.update(dt)
            elif tile.is_occupied() and tile.entity.type == None:
                tile.entity.update(dt)

        self.remove_timeout_entity()
        
    def render(self, screen):
        RenderTurn(screen, 'SelectPullState', self.turn, self.currentTurnOwner)
        RenderEntityStats(screen, self.player, self.enemy)
        RenderSelectedCard(screen, self.player.selectedCard, self.enemy.selectedCard)
        RenderDescription(screen, f"Current Action: {self.effect.type}", f"Owner: {self.effectOwner.value}")
        RenderFieldSelection(screen, self.field, self.availablePullTile, self.selectPullTile, self.effectOwner)
        

        