from settings import *
from timer import Timer
from math import sin
from random import randint
import pygame
from support import *
from powerup import *
class Sprite(pygame.sprite.Sprite):

    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, bullet_surf, pos, direction, groups, collision_sprites, game):
       super().__init__(groups)
       self.image = bullet_surf
       self.rect = self.image.get_rect(center=pos)
       self.direction = direction
       self.speed = 600
       self.game = game
       self.collision_sprites = collision_sprites
       self.rect.x += self.direction * 60

    def update(self, dt):
        self.rect.x += self.direction * self.speed * dt # Di chuyển viên đạn
        # for sprite in self.collision_sprites: # Kiểm tra va chạm với vật cản (nếu có)
        #     if self.rect.colliderect(sprite.rect):
        #         self.kill()
        if self.rect.right < 0 or self.rect.left > WINDOW_WIDTH:
            self.kill()

        for enemy in self.game.enemy_sprites:
            if self.rect.colliderect(enemy.rect):
                enemy.destroy()  # Gọi destroy để tiêu diệt quái vật (có hiệu ứng nếu có)
                self.kill()  # Hủy viên đạn sau khi trúng quái vật
                # Phát âm thanh va chạm (nếu có)
                if 'impact' in self.game.audio:
                    self.game.audio['impact'].play()
                break  # Thoát vòng lặp sau khi trúng một quái vật

        if self.rect.right < 0 or self.rect.left > WINDOW_WIDTH:  # Tự huỷ nếu ra ngoài màn hình
            self.kill()


class Fire(Sprite):
    def __init__(self, surf, pos, groups, player):
        super().__init__(pos, surf, groups)
        self.player = player
        self.image=surf
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
    def __init__(self, pos, groups, collision_sprites, frames, game,audio,bullet_surf,fire_surf):
        super().__init__(frames, pos, groups)
        self.game = game
        self.audio=audio
        self.flip = False # biến canh để nhân vật qua left or right
        self.direction = pygame.Vector2()
        self.collision_sprites = collision_sprites
        self.speed = 400
        self.bullet_surf = bullet_surf
        self.fire_surf = fire_surf  # Lưu fire_surf
        self.gravity = 50
        self.on_floor = False
        self.shoot_timer = Timer(500)
        self.can_shoot = False
        self.fall_timer = 0
        self.last_shot = 0
        self.laser_active = False
        self.laser_timer = None

    def activate_laser(self):
        self.laser_active = True
        self.laser_timer = Timer(10000, func=self.deactivate_laser, autostart=True) # Bật hiệu ứng laser trong 5000ms (5 giây)
        
    def deactivate_laser(self):
        self.laser_active = False

    def draw_laser(self, surface):
        if not self.laser_active:
            return
        offset = self.game.all_sprites.offset # Lấy offset từ camera (được tính trong AllSprites.draw)
        start_pos = (self.rect.centerx + offset.x, self.rect.centery + offset.y)# lấy vị trí nhân vật ở màn hình 
        mouse_pos = pygame.mouse.get_pos()#lấy vị trí chuột
        dx = mouse_pos[0] - start_pos[0] # Tính vector từ start_pos đến vị trí chuột
        dy = mouse_pos[1] - start_pos[1] # Tính vector từ start_pos đến vị trí chuột
        length = math.hypot(dx, dy) 
        if length == 0:
            length = 1
        dx /= length
        dy /= length
        laser_length = 800 # Độ dài của laser (điều chỉnh ở đây)
        end_pos = (start_pos[0] + dx * laser_length, start_pos[1] + dy * laser_length)
        pygame.draw.line(surface, (255, 0, 0), start_pos, end_pos, 5) #vẽ đường l
       
    def check_laser_collision(self):
        if not self.laser_active:
            return
        offset = self.game.all_sprites.offset # Lấy offset từ camera
        start_pos = (self.rect.centerx + offset.x, self.rect.centery + offset.y) # Tọa độ laser trên màn hình
        mouse_pos = pygame.mouse.get_pos()
        dx = mouse_pos[0] - start_pos[0]
        dy = mouse_pos[1] - start_pos[1]
        length = math.hypot(dx, dy)
        if length == 0:
            length = 1
        dx /= length
        dy /= length
        laser_length = 800  # Độ dài laser
        end_pos = (start_pos[0] + dx * laser_length, start_pos[1] + dy * laser_length)
        for enemy in self.game.enemy_sprites:  # Kiểm tra va chạm với tất cả quái vật trong enemy_sprites
            enemy_screen_rect = enemy.rect.copy() # Chuyển tọa độ của quái vật sang tọa độ màn hình
            enemy_screen_rect.topleft = (enemy.rect.x + offset.x, enemy.rect.y + offset.y)
            if enemy_screen_rect.clipline(start_pos, end_pos): # Kiểm tra xem laser có giao với hình chữ nhật của quái vật không
                enemy.destroy()  # Gọi hàm destroy thay vì kill
                if 'impact' in self.audio:# Nếu bạn muốn thêm âm thanh khi tiêu diệt
                    self.audio['impact'].play()

    def check_collision_with_powerup(self, powerups):
        collided_powerups = pygame.sprite.spritecollide(self, powerups, True)
        for power in collided_powerups:
            if isinstance(power, LaserPowerUp):  # Kiểm tra nếu là LaserPowerUp thì kích hoạt chế độ laser
                self.activate_laser()
            else:
                self.can_shoot = True

    def inp(self):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        if (keys[pygame.K_w] or keys[pygame.K_UP]) and self.on_floor: # Nhảy lên với khoảng cách cách với vị trí đang đứng là 50
            self.direction.y = -35
        current_time = pygame.time.get_ticks()
        if keys[pygame.K_SPACE] and self.can_shoot and current_time - self.last_shot > 300:  # cách nhau 300ms mỗi lần bắn
            self.shoot()
            self.last_shot = current_time

    def shoot(self):
        bullet_direction = -1 if self.flip else 1 # Xác định hướng bắn dựa trên trạng thái flip của nhân vật
        pos = self.rect.center # Tính vị trí spawn của đạn dựa trên hướng (từ tâm nhân vật)
        if bullet_direction == 1:
            x = pos[0] 
        else:
            x = pos[0] - self.bullet_surf.get_width()
        bullet_pos = (x, pos[1])
        Bullet(self.bullet_surf, bullet_pos, bullet_direction, self.groups(), self.collision_sprites, self.game)# Tạo đạn
        Fire(self.fire_surf, pos, self.groups(), self) # Tạo hiệu ứng lửa (nếu muốn)
        self.audio['shoot'].play() # Phát âm thanh bắn

    def move(self, dt):
        self.rect.x += self.direction.x * self.speed * dt  # Di chuyển theo trục x
        self.collision('horizontal')
        self.direction.y += self.gravity * dt # Di chuyển theo trục y
        self.rect.y += self.direction.y
        self.collision('vertical')

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.rect):
                if direction == 'horizontal':
                    if self.direction.x > 0: #di chuuyển qua phải (đến khi chạm vật)
                        self.rect.right = sprite.rect.left
                    elif self.direction.x < 0: #di chuyển qua trái (đến khi chạm vật)
                        self.rect.left = sprite.rect.right
                else:
                    if self.direction.y > 0: #di chuyển lên xuống
                        self.rect.bottom = sprite.rect.top
                        self.direction.y = 0 #chạm vật thể
                    elif self.direction.y < 0:
                        self.rect.top = sprite.rect.bottom
                        self.direction.y = 0

    def check_on_floor(self):
        bottom_rect = pygame.Rect(0, 0, self.rect.width, 2)
        bottom_rect.midtop = self.rect.midbottom
        level_rects = [sprite.rect for sprite in self.collision_sprites]
        self.on_floor = True if bottom_rect.collidelist(level_rects) >= 0 else False

    def animate(self, dt):
        if not self.on_floor:  # Nếu đang nhảy
            self.flip = self.direction.x < 0 if self.direction.x else self.flip  # Cập nhật hướng xoay khi di chuyển
            self.image = self.frames[-2]  # Dùng frame cố định khi nhảy
        elif self.direction.x:  # Nếu đang di chuyển trên mặt đất
            self.frames_index += self.annotation_speed * dt
            self.flip = self.direction.x < 0  # Cập nhật hướng xoay
            self.image = self.frames[int(self.frames_index) % len(self.frames)]
        else:  # Nếu đứng yên trên mặt đất
            self.frames_index = 0
            self.image = self.frames[0]
        self.image = pygame.transform.flip(self.image, self.flip, False)

    def update(self, dt):
        self.shoot_timer.update()
        if self.laser_active and self.laser_timer:  # Cập nhật timer của laser nếu đang hoạt động
            self.laser_timer.update()
        self.check_on_floor()
        self.check_collision_with_powerup(self.game.powerups)
        self.inp()
        self.move(dt)
        self.animate(dt)
        self.check_laser_collision()
        
        if not self.on_floor > 0 and self.rect.top > WINDOW_HEIGHT: # Kiểm tra rơi khỏi màn hình (code đã có)
            self.fall_timer += dt
            if self.direction.y > 0 and self.fall_timer >= 3:
                self.game.game_over()
        else:
            self.fall_timer = 0
