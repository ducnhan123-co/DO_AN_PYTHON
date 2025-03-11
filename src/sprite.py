from settings import *
from timer import Timer
from math import sin
from random import randint
import pygame

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, direction, groups, collision_sprites):
        super().__init__(groups)
        self.image = pygame.Surface((10, 5))
        self.image.fill('blue')
        self.rect = self.image.get_rect(center=pos)
        self.direction = direction
        self.speed = 600
        self.collision_sprites = collision_sprites
        # Vị trí ban đầu (nếu muốn “nảy” ra xa nhân vật)
        self.rect.x += self.direction * 60

    def update(self, dt):
        # Di chuyển viên đạn
        self.rect.x += self.direction * self.speed * dt

        # Kiểm tra va chạm với vật cản (nếu có)
        for sprite in self.collision_sprites:
            if self.rect.colliderect(sprite.rect):
                self.kill()

        # Tự huỷ nếu ra ngoài màn hình
        if self.rect.right < 0 or self.rect.left > WINDOW_WIDTH:
            self.kill()


class Fire(Sprite):
    def __init__(self, surf, pos, groups, player):
        super().__init__(pos, surf, groups)
        self.player = player
        self.flip = player.flip
        self.timer = Timer(100, autostart=True, func=self.kill)
        self.y_offset = pygame.Vector2(0.8)
        if self.player.flip:
            self.rect.midright = self.player.rect.midleft + self.y_offset
            self.image = pygame.transform.flip(self.image, True, False)
        else:
            self.rect.midleft = self.player.rect.midright + self.y_offset

    def update(self, _):
        self.timer.update()
        if self.player.flip:
            self.rect.midright = self.player.rect.midleft + self.y_offset
        else:
            self.rect.midleft = self.player.rect.midright + self.y_offset
        if self.flip != self.player.flip:
            self.kill()

class AnimatedSprite(Sprite):
    def __init__(self, frames, pos, groups):
        self.frames = frames
        self.frames_index = 0
        self.annotation_speed = 10
        super().__init__(pos, self.frames[self.frames_index], groups)

    def animate(self, dt):
        self.frames_index += self.annotation_speed * dt
        self.image = self.frames[int(self.frames_index) % len(self.frames)]

class Enemy(AnimatedSprite):
    def __init__(self, frames, pos, groups):
        super().__init__(frames, pos, groups)
        self.death_timer = Timer(1000, func=self.kill)

    def destroy(self):
        self.death_timer.activate()
        self.annotation_speed = 0
        self.image = pygame.mask.from_surface(self.image).to_surface()
        self.image.set_colorkey('black')

    def update(self, dt):
        self.death_timer.update()
        if not self.death_timer:
            self.move(dt)
            self.animate(dt)
        self.constraint()

class Bee(Enemy):
    def __init__(self, frames, pos, groups, speed):
        super().__init__(frames, pos, groups)
        self.speed = speed
        self.amplitude = randint(500, 600)
        self.freq = randint(300, 500)

    def move(self, dt):
        self.rect.x -= self.speed * dt
        self.rect.y += sin(pygame.time.get_ticks() / self.freq) * self.amplitude * dt

    def constraint(self):
        if self.rect.right <= 0:
            self.kill()

class Worm(Enemy):
    def __init__(self, frames, rect, groups):
        super().__init__(frames, rect.topleft, groups)
        self.rect.bottomleft = rect.bottomleft
        self.main_rect = rect
        self.speed = randint(100, 200)
        self.direction = 1

    def move(self, dt):
        self.rect.x += self.speed * self.direction * dt

    def constraint(self):
        if not self.main_rect.contains(self.rect):
            self.direction *= -1
            self.frames = [pygame.transform.flip(surf, True, False) for surf in self.frames]

class Player(AnimatedSprite):
    def __init__(self, pos, groups, collision_sprites, frames, game):
        super().__init__(frames, pos, groups)
        self.game = game
        self.flip = False # biến canh để nhân vật qua left or right
        self.direction = pygame.Vector2()
        self.collision_sprites = collision_sprites
        self.speed = 400
        self.gravity = 50
        self.on_floor = False
        self.shoot_timer = Timer(500)
        self.can_shoot = False
        self.fall_timer = 0
        self.last_shot = 0
       

    def check_collision_with_powerup(self, powerups):
        collided_powerups = pygame.sprite.spritecollide(self, powerups, True)
        if collided_powerups:
            self.can_shoot = True

    def inp(self):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        
        # Nhảy lên với khoảng cách cách với vị trí đang đứng là 50
        if (keys[pygame.K_w] or keys[pygame.K_UP]) and self.on_floor:
            self.direction.y = -35

        current_time = pygame.time.get_ticks()
        if keys[pygame.K_SPACE] and self.can_shoot and current_time - self.last_shot > 300:  # cách nhau 300ms mỗi lần bắn
            self.shoot()
            self.last_shot = current_time

    def shoot(self):
        bullet_direction = -1 if self.flip else 1
        Bullet(self.rect.center, bullet_direction, self.groups(),self.collision_sprites)

    def move(self, dt):
        # Di chuyển theo trục x
        self.rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        # Di chuyển theo trục y
        self.direction.y += self.gravity * dt
        self.rect.y += self.direction.y
        self.collision('vertical')

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.rect):
                if direction == 'horizontal':
                    if self.direction.x > 0:
                        self.rect.right = sprite.rect.left
                    elif self.direction.x < 0:
                        self.rect.left = sprite.rect.right
                else:
                    if self.direction.y > 0:
                        self.rect.bottom = sprite.rect.top
                        self.direction.y = 0
                    elif self.direction.y < 0:
                        self.rect.top = sprite.rect.bottom
                        self.direction.y = 0

    def check_on_floor(self):
        bottom_rect = pygame.Rect(0, 0, self.rect.width, 2)
        bottom_rect.midtop = self.rect.midbottom
        level_rects = [sprite.rect for sprite in self.collision_sprites]
        self.on_floor = True if bottom_rect.collidelist(level_rects) >= 0 else False

    def animate(self, dt):
        if self.direction.x:
            self.frames_index += self.annotation_speed * dt
            self.flip = self.direction.x < 0 # qua phải thì true trái thì false
        else:
            self.frames_index = 0
        self.image = self.frames[int(self.frames_index) % len(self.frames)]
        self.image = pygame.transform.flip(self.image, self.flip, False)

    def update(self, dt):
        self.shoot_timer.update()
        self.check_on_floor()
        self.check_collision_with_powerup(self.game.powerups)
        self.inp()
        self.move(dt)
        self.animate(dt)
        # Kiểm tra rơi khỏi màn hình
        if not self.on_floor and self.direction.y > 0 and self.rect.top > WINDOW_HEIGHT:
            self.fall_timer += dt  # Tăng thời gian rơi
            if self.fall_timer >= 4:  # Nếu rơi hơn 3 giây
                self.game.game_over()  # Gọi hàm kết thúc trò chơi
        else:
            self.fall_timer = 0  # Reset nếu không rơi
