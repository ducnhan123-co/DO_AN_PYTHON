from settings import *
import pygame
from powerup import PowerUp,Bullet
class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)


class AnimatedSprite(Sprite):
    def __init__(self, frames, pos, groups):
        self.frames, self.frames_index, self.annotation_speed = frames, 0, 10
        super().__init__(pos, self.frames[self.frames_index], groups)

    def animate(self, dt):
        self.frames_index += self.annotation_speed * dt
        self.image = self.frames[int(self.frames_index) % len(self.frames)]


class Bee(AnimatedSprite):
    def __init__(self, frames, pos, groups):
        super().__init__(frames, pos, groups)

    def update(self, dt):
        self.animate(dt)

class Worm(AnimatedSprite):
    def __init__(self, frames, pos, groups):
        super().__init__(frames, pos, groups)

    def update(self, dt):
        self.animate(dt)


class Player(AnimatedSprite):
    def __init__(self, pos, groups, collision_sprites, frames,game):
        super().__init__(frames, pos,groups)
        self.game = game
        self.flip = False # biến canh để nhân vật qua left or right

        # movement and collision
        self.direction = pygame.Vector2()
        self.collision_sprites = collision_sprites
        self.speed = 400
        # Thiết kế trọng lực khi nhảy lên và nhảy xuống
        self.gravity = 50
        self.on_floor = False
        self.can_shoot= False
        # self.all_sprites = groups
        self.last_shot = 0
        self.fall_timer = 0
    
    # Kiểm tra phím bấm để điều khiển nhân vật.
    def inp(self):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        
        # Nhảy lên với khoảng cách cách với vị trí đang đứng là 18
        if (keys[pygame.K_w] or keys[pygame.K_UP]) and self.on_floor:
            self.direction.y = -30

        current_time = pygame.time.get_ticks()
        if keys[pygame.K_SPACE] and self.can_shoot and current_time - self.last_shot > 300:  # cách nhau 300ms mỗi lần bắn
            self.shoot()
            self.last_shot = current_time

    def shoot(self):
        bullet_direction = -1 if self.flip else 1
        Bullet(self.rect.center, bullet_direction, self.groups(),self.collision_sprites)
        
    def check_collision_with_powerup(self, powerups):
        collided_powerups = pygame.sprite.spritecollide(self, powerups, True)  # 🔹 Xóa power-up khi va chạm
        if collided_powerups:
            self.can_shoot = True  # 🔹 Player có thể bắn đạn

    # Di chuyển nhân vật theo hướng nhập từ bàn phím
    def move(self, dt):
        # Trục x
        self.rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')

        # Trục y
        self.direction.y += self.gravity * dt
        self.rect.y += self.direction.y
        self.collision('vertical')

    # Ngăn nhân vật đi xuyên qua vật thể khác.
    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.rect):
                if direction == 'horizontal':
                    if self.direction.x > 0:  # Đang đi sang phải
                        self.rect.right = sprite.rect.left
                    elif self.direction.x < 0:  # Đang đi sang trái
                        self.rect.left = sprite.rect.right
                else:  # direction == 'vertical'
                    if self.direction.y > 0:  # Đang đi xuống
                        self.rect.bottom = sprite.rect.top
                        self.direction.y = 0  # Player sẽ dừng lại khi gặp platform
                    elif self.direction.y < 0:  # Đang đi lên
                        self.rect.top = sprite.rect.bottom
                        self.direction.y = 0

    def check_on_floor(self):
        bottom_rect = pygame.Rect(0, 0, self.rect.width, 2)
        bottom_rect.midtop = self.rect.midbottom  # Di chuyển đúng vị trí
        level_rects = [sprite.rect for sprite in self.collision_sprites]
        self.on_floor = True if bottom_rect.collidelist(level_rects) >= 0 else False

    # @overide
    # thiết kế phần chân player if move theo left or right thì chuyển động chân còn k thì đứng yên
    def animate(self, dt):
        if self.direction.x:
            self.frames_index += self.annotation_speed * dt
            self.flip = self.direction.x < 0 # qua phải thì true trái thì false
        else:
            self.frames_index = 0
        self.image = self.frames[int (self.frames_index) % len(self.frames)]
        self.image = pygame.transform.flip(self.image, self.flip, False)

    

    def update(self, dt):
        self.check_on_floor()
        self.check_collision_with_powerup(self.collision_sprites)
        self.inp()
        self.move(dt)
        self.animate(dt)


        if not self.on_floor and self.direction.y > 0 and self.rect.top > WINDOW_HEIGHT:
            self.fall_timer += dt  # Tăng thời gian rơi
            if self.fall_timer >= 2:  # Nếu rơi hơn 3 giây
                self.game.game_over()  # Gọi hàm kết thúc trò chơi
        else:
            self.fall_timer = 0  # Reset nếu không rơi




