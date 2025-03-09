from settings import * 
from sprite import *
from groups import *
from support import *
from powerup import PowerUp
import random
import math
print(pygame.version.ver)
# B1
class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Platformer Space Runner')
        self.clock = pygame.time.Clock()
        self.running = True
        self.background = pygame.image.load('data/graphics/Background.png').convert()
        # groups 
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()

        #loadgame
        self.load_assets()
        self.setup()

    def load_assets(self):
        # graphics
        self.player_frames = import_folder('images', 'player')
        self.bullet_surf = import_image('images','gun', 'bullet')
        self.fire_surf = import_image('images','gun', 'fire')
        self.bee_frames = import_folder('images', 'enemies', 'bee')
        self.worm_frames = import_folder('images', 'enemies', 'worm')

         # ✅ Load ảnh game over
        self.game_over_bg = pygame.image.load('data/graphics/prank.jpg').convert()
        # sounds
        self.audio = import_audio('audio')
        self.audio['music'].play()

    def setup(self):
        tmx_map = load_pygame(join('data','maps', 'new_world_3.tmx'))

        # Create map
        for x, y, image in tmx_map.get_layer_by_name('Main').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, (self.all_sprites, self.collision_sprites))
        
        # Create các đô họa từ layer có tên Decoration
        for x, y, image in tmx_map.get_layer_by_name('Decoration').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)
        
        # Create player
        for obj in tmx_map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites, self.player_frames,self)

        Bee(self.bee_frames, (500,600), self.all_sprites)
        Worm(self.worm_frames, (700,600), self.all_sprites)

         
        PowerUp((random.randint(50, WINDOW_WIDTH - 50), random.randint(50, WINDOW_HEIGHT - 50)),(self.all_sprites, self.collision_sprites,self.powerups))

    def game_over(self):
        print("Game Over!")  # Thông báo game over

        # ✅ Dừng nhạc nền
        if 'music' in self.audio:
            self.audio['music'].stop()

        # ✅ Kiểm tra xem prank.wav đã được load vào self.audio chưa
        if 'prank' in self.audio:
            self.audio['prank'].play(loops=-1)  # Lặp vô hạn
        else:
            try:
                game_over_sound = pygame.mixer.Sound('audio/prank.wav')  # Đúng đường dẫn
                game_over_sound.play(loops=-1)
            except Exception as e:
                print(f"Lỗi phát nhạc game over: {e}")

        # ✅ Hiển thị hình ảnh nền game over full màn hình
        game_over_resized = pygame.transform.scale(self.game_over_bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.display_surface.blit(game_over_resized, (0, 0))

        # ✅ Hiển thị chữ "Bạn thua rồi!"
        font = pygame.font.Font(None, 64)
        text = font.render("BẠN THUA RỒI!!!!!!!!!!!!!!!!!!!!!!", True, (255, 0, 0))
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.display_surface.blit(text, text_rect)

        pygame.display.update()
        pygame.time.delay(4000)  # Đợi 2 giây rồi thoát
        self.running = False






    def run(self):
        while self.running:
            dt = self.clock.tick(FRAMERATE) / 1000 

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False 
            
             # ✅ Vẽ background trước
            self.display_surface.blit(self.background, (0, 0))

            # gọi tất cả update(mà update thường có sự kiện bàn phím,di chuyển nhân vật)
            self.all_sprites.update(dt)

            # draw 
            # self.display_surface.fill(BG_COLOR)
            self.all_sprites.draw(self.player.rect.center)
            pygame.display.update()
        
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()