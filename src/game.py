from settings import *
from sprite import *
from groups import *
from support import *
from timer import Timer
from powerup import PowerUp
from powerup import LaserPowerUp
import pygame
from os.path import join
from pytmx.util_pygame import load_pygame
from random import randint

class Game:
    def __init__(self):
        # Khởi tạo Pygame và thiết lập màn hình hiển thị 
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Platformer Space Runner')
        self.clock = pygame.time.Clock()
        self.running = True

        # Vị trí X của background
        self.bg_x = 0  
        self.bg_speed = 100  # Tốc độ di chuyển của background (pixel/giây)

        # Tạo các nhóm sprite,mấy cái nhân vật đồ
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites  = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()

        # Set up tài nguyên để chạy game
        self.load_assets()
        self.setup()

        # Tạo bộ đếm thời gian để canh chỉnh thơi gian ong respawn
        self.bee_timer = Timer(1000, func=self.create_bee, autostart=True, repeat=True)

    def load_assets(self):
        # Tải các tài nguyên đồ họa
        self.player_frames = import_folder('images', 'player')
        self.bullet_surf = import_image('images', 'gun', 'bullet')
        self.fire_surf = import_image('images', 'gun', 'fire')
        self.bee_frames = import_folder('images', 'enemies', 'bee')
        self.worm_frames = import_folder('images', 'enemies', 'worm')
        # Tải hình nền
        self.background = pygame.image.load('data/graphics/Summer2.png').convert() #hình nên chính khi chơi
        self.background = pygame.transform.scale(self.background, (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.display_surface.blit(self.background, (0, 0))  # Vẽ background cố định
        self.game_over_bg = pygame.image.load('data/graphics/tilesetOpenGameBackground.png').convert() #hình nền khi thua :))

        # Tải âm thanh chính
        self.audio = import_audio('audio')
        if 'game_menu' in self.audio:
            self.audio['game_menu'].stop()
        # Phát nhạc cho game
        self.audio['music'].play(loops=-1)

    def setup(self):
        # Tải bản đồ và tính toán kích thước level
        tmx_map = load_pygame(join('data','maps', 'new_world_3.tmx'))
        self.level_width = TILE_SIZE * tmx_map.width
        self.level_height = TILE_SIZE * tmx_map.height

        # Tạo các tile từ layer Main (gạch,sàn có xử lý đụng độ)
        for x, y, image in tmx_map.get_layer_by_name('Main').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, (self.all_sprites, self.collision_sprites))
        
        # Tạo các đối tượng từ layer Decoration ,đi xuyên qua được (cho đẹp thôi)
        for x, y, image in tmx_map.get_layer_by_name('Decoration').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)
        
        # Tạo các đối tượng từ layer Entities: Player và Worm 
        for obj in tmx_map.get_layer_by_name('Entities'): #nhân vật chính game
            if obj.name == 'Player':
                self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites, self.player_frames, self,self.audio)
            elif obj.name == 'Worm': #mấy con quái
                Worm(self.worm_frames, pygame.Rect(obj.x, obj.y, obj.width, obj.height), (self.all_sprites, self.enemy_sprites))
        
        # Sinh ra một năng lực ngẫu nhiên chạm vào là biến mất và bắn bằng SPACE được
        PowerUp((randint(50, WINDOW_WIDTH - 50), randint(50, WINDOW_HEIGHT - 50)), 
                (self.all_sprites, self.collision_sprites, self.powerups))
        
        LaserPowerUp((randint(50, WINDOW_WIDTH - 50), randint(50, WINDOW_HEIGHT - 50)), 
                 (self.all_sprites, self.collision_sprites, self.powerups))
    
    def create_bee(self):
        # Tạo một con Bee mới và thêm vào các nhóm sprite
        Bee(
            frames=self.bee_frames,
            pos=(self.level_width + WINDOW_WIDTH, randint(0, self.level_height)),
            groups=(self.all_sprites, self.enemy_sprites),
            speed=randint(250, 500)
        )

#chưa dùng
    def create_bullet(self, pos, direction):
        # Tính vị trí spawn của đạn dựa theo hướng
        if direction == 1:
            x = pos[0] + 34
        else:
            x = pos[0] - 34 - self.bullet_surf.get_width()
        # Tạo đạn và hiệu ứng lửa, phát âm thanh bắn
        Bullet(self.bullet_surf, (x, pos[1]), direction, (self.all_sprites, self.bullet_sprites))
        Fire(self.fire_surf, pos, self.all_sprites, self.player)
        self.audio['shoot'].play()


    def collision(self):
        # Xử lý va chạm giữa đạn và kẻ thù
        for bullet in self.bullet_sprites:
            hits = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
            if hits:
                self.audio['impact'].play()
                bullet.kill()
                for hit in hits:
                    hit.destroy()
        
        # Nếu người chơi va chạm với kẻ thù -> game over
        if pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask):
            self.game_over()

    def game_over(self):
        print("Game Over!")
        # Dừng nhạc nền
        if 'music' in self.audio:
            self.audio['music'].stop()
        # Phát nhạc game over
        if 'prank' in self.audio:
            self.audio['prank'].play(loops=-1)
        else:
            try:
                game_over_sound = pygame.mixer.Sound('audio/prank.wav')
                game_over_sound.play(loops=-1)
            except Exception as e:
                print(f"Lỗi phát nhạc game over: {e}")
        # Hiển thị ảnh game over với hiệu ứng rung
        prank_image = pygame.transform.scale(self.game_over_bg, (WINDOW_WIDTH-100, WINDOW_HEIGHT-100))
        center_x = (WINDOW_WIDTH // 2) - (prank_image.get_width() // 2)
        center_y = (WINDOW_HEIGHT // 2) - (prank_image.get_height() // 2)
        for _ in range(15):
            offset_x = randint(-10, 10)
            offset_y = randint(-10, 10)
            self.display_surface.fill((0, 0, 0))
            self.display_surface.blit(prank_image, (center_x + offset_x, center_y + offset_y))
            pygame.display.update()
            pygame.time.delay(100)
        game_over_resized = pygame.transform.scale(self.game_over_bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.display_surface.blit(game_over_resized, (0, 0))
        font = pygame.font.Font(None, 64)
        text = font.render("GAME OVER MY FRIEND!!!!!!", True, (255, 0, 0))
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.display_surface.blit(text, text_rect)
        pygame.display.update()
        pygame.time.delay(4000)
        self.running = False

    def run(self):
        # Vòng lặp chính của game
        while self.running:
            dt = self.clock.tick(FRAMERATE) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            # Cập nhật bộ đếm thời gian và các sprite
            self.bee_timer.update()
            self.all_sprites.update(dt)
            self.collision()
            # Vẽ background
            if self.background:
                self.display_surface.blit(self.background, (0, 0))
            else:
                self.display_surface.fill(BG_COLOR)

            # Cập nhật vị trí background
            self.bg_x -= self.bg_speed * dt  

            # Nếu background cuộn hết, reset lại vị trí
            if self.bg_x <= -WINDOW_WIDTH:
                self.bg_x = 0  

            # Vẽ background (lặp lại background để tạo hiệu ứng vô hạn)
            self.display_surface.blit(self.background, (self.bg_x, 0))
            self.display_surface.blit(self.background, (self.bg_x + WINDOW_WIDTH, 0))  # Background lặp lại

            # Vẽ tất cả các sprite
            self.all_sprites.draw(self.player.rect.center)
            if self.player.laser_active:
                self.player.draw_laser(self.display_surface)
        
            pygame.display.update()
        pygame.quit()

# if __name__ == '__main__':
#     while True:
#         choice = menu_game.menu_game()  # Gọi menu và lấy lựa chọn từ người chơi

#         if choice == "play":
#             pygame.mixer.stop()  # Dừng tất 

#             game = Game()  # Khởi động game
#             game.run()
#         elif choice == "settings":
#             print("Chưa có cài đặt, cần thêm menu_settings.py")
#         elif choice == "exit":
#             print("Thoát game.")
#             break  # Dừng chương trình 