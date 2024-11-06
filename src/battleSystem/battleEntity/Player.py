from src.battleSystem.battleEntity.Entity import Entity
from src.dependency import *
from src.battleSystem.Effect import Effect


class Player(Entity):
    def __init__(self, name, job, animationList ,image=None):
        super().__init__(name, animationList, image=image)
        self.health = 30
        self.job = job


    def update(self, dt):
        # Implement player-specific update logic here
        super().update(dt)
        pass

    def render(self, screen, x, y):
        # Call the parent render method
        super().render(screen, x, y, (0, 255, 0))

        # Add player-specific rendering logic here if needed
        # screen.blit(self.image, (x, y))
        pass
