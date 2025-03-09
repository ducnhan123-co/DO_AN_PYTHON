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
        # Lơ lửng lên xuống
        self.rect.y = self.start_y + math.sin(pygame.time.get_ticks() * 0.005) * 5

        # Nhấp nháy
        self.timer += dt
        if self.timer > 0.3:
            self.image.set_alpha(50 if self.image.get_alpha() == 255 else 255)
            self.timer = 0

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, direction, groups, collision_sprites):
        super().__init__(groups)
        self.image = pygame.Surface((10, 5))
        self.image.fill('blue')
        self.rect = self.image.get_rect(center=pos)
        self.direction = direction
        self.speed = 600
        self.collision_sprites = collision_sprites  

        self.rect.x +=self.direction * 60
       

    def update(self, dt):
        self.rect.x += self.direction * self.speed * dt

        # Kiểm tra va chạm với các vật cản thực sự (không phải Decoration)
        for sprite in self.collision_sprites:
            if self.rect.colliderect(sprite.rect):
                self.kill()  # Nếu đạn chạm vào vật thể cứng, nó sẽ biến mất.

        # Nếu đạn ra khỏi màn hình, tự hủy
        if self.rect.right < 0 or self.rect.left > WINDOW_WIDTH:
            self.kill()
