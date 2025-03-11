import pygame
from settings import *
import math

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 255, 0), (15, 15), 15)
        self.rect = self.image.get_rect(center=pos)
        self.timer = 0
        self.start_y = pos[1]

    def update(self, dt):
        # Hiệu ứng lơ lửng
        self.rect.y = self.start_y + math.sin(pygame.time.get_ticks() * 0.005) * 5
