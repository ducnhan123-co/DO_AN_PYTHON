import pygame  # Đảm bảo import pygame trước khi dùng
from settings import *
from support import *
# Khởi tạo pygame
pygame.init()  # Cần gọi trước khi tạo cửa sổ game

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Menu Game")

# Màu sắc
WHITE = (255,255,255)
BLACK = (0,0,0)
GRAY = (100,100,100)
BLUE = (50,150,255)

# FONT
font = pygame.font.Font(None, 50)

# Danh sách nút menu
menu_items = ["Play", "Settings", "Exit"]
selected_index = 0  # Chỉ mục đang chọn

# Vị trí X của background
bg_x = 0  
bg_speed = 100  # Tốc độ di chuyển của background (pixel/giây)

# Load background
try:
    background = pygame.image.load("data/graphics/tilesetOpenGameBackground.png")
    background = pygame.transform.scale(background, (WINDOW_WIDTH, WINDOW_HEIGHT))
    screen.blit(background, (WINDOW_WIDTH, WINDOW_HEIGHT))
except pygame.error as e:
    print(f"Lỗi khi load ảnh background: {e}")
    background = None  # Gán None nếu load ảnh thất bại
audio = import_audio('audio')
if 'game_menu' in audio:
    audio['game_menu'].play(loops=-1)  # Phát nhạc menu lặp vô hạn chỉ 1 lần

# Vẽ 
def draw_menu():
    """Vẽ menu lên màn hình với background di chuyển từ trái sang phải."""
    global bg_x
    
    screen.fill(WHITE)  # Xóa màn hình trước khi vẽ lại menu
    if background:
        # Cập nhật vị trí background
        bg_x += bg_speed * (1 / FRAMERATE)  # Di chuyển sang phải

        # Nếu background cuộn hết, reset lại vị trí
        if bg_x >= WINDOW_WIDTH:
            bg_x = 0

        # Vẽ background hai lần để tạo hiệu ứng cuộn liên tục
        screen.blit(background, (bg_x, 0))
        screen.blit(background, (bg_x - WINDOW_WIDTH, 0))  # Background thứ hai nằm bên trái

    for i, text in enumerate(menu_items):
        color = BLUE if i == selected_index else BLACK
        label = font.render(text, True, color)
        x = WINDOW_WIDTH // 2 - label.get_width() // 2
        y = 200 + i * 80
        screen.blit(label, (x, y))
    
    pygame.display.flip()

# Giao diện start
def menu_game():
    global selected_index
    running = True
    while running:
        draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return "exit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(menu_items)
                elif event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(menu_items)
                elif event.key == pygame.K_RETURN:
                    if selected_index == 0:
                        return "play"
                    elif selected_index == 1:
                        return "settings"
                    elif selected_index == 2:
                        return "exit"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                for i, text in enumerate(menu_items):
                    item_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, 200 + i * 80, 200, 50)
                    if item_rect.collidepoint(x, y):
                        if i == 0:
                            return "play"
                        elif i == 1:
                            return "settings"
                        elif i == 2:
                            return "exit"
    return "exit"

# Menu setting


# Menu nhỏ khi đang chơi game
# def sub_menu():
