import pygame  
from settings import *
from support import *

# Khởi tạo pygame
pygame.init()

# Khởi tạo màn hình
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Menu Game")

# Màu
WHITE = (255,255,255)
BLACK = (0,0,0)
GRAY = (100,100,100)
BLUE = (50,150,255)
BGCOLOR = (27, 31, 102)  
BUTTON_COLOR = (39, 231, 201)  

# set font
font = pygame.font.Font('data/font/8-BIT WONDER.TTF', 20)
title_font = pygame.font.Font('data/font/8-BIT WONDER.TTF', 80)
menu_font = pygame.font.Font('data/font/8-BIT WONDER.TTF', 40)
credit_font = pygame.font.Font('data/font/8-BIT WONDER.TTF', 70)

# Tải background
try:
    background = pygame.image.load("data/graphics/tilesetOpenGameBackground.png")
    background = pygame.transform.scale(background, (WINDOW_WIDTH, WINDOW_HEIGHT))
except pygame.error as e:
    print(f"Lỗi khi load ảnh background: {e}")
    background = None  

# Tải Audio
audio = import_audio('audio')
if 'ni_idea' in audio:
    audio['ni_idea'].play(loops=-1)

# Hàm vẽ chữ phát sáng neon
def draw_glow_text(text, font, color, x, y):
    glow_color = (min(color[0] + 50, 255), min(color[1] + 50, 255), min(color[2] + 50, 255))  # Giới hạn max 255
    for dx in range(-3, 4):
        for dy in range(-3, 4):
            glow_text = font.render(text, True, glow_color)
            screen.blit(glow_text, (x + dx, y + dy))
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))


#Lớp tạo nút giao diện
class Button:
    # self, nội dung text, tọa độ x, y, độ rộng độ cao, màu ban đầu, màu sau khi hover, kiểu font
    def __init__(self, text, x, y, width, height, base_color, hover_color, font):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.base_color = base_color
        self.hover_color = hover_color
        self.font = font
        self.rect = pygame.Rect(x, y, width, height)
    
    def draw(self, screen, text_color):
        """Vẽ nút với màu chữ thay đổi"""
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(text_surface, text_rect)

    def is_clicked(self):
        """Kiểm tra xem nút có bị click hay không"""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        return self.rect.collidepoint(mouse_x, mouse_y)

# Màn hình chính
class GameMenu:
    def __init__(self, selected_index=0, hover_index=0):
        self.selected_index = selected_index  # Chỉ số nút được chọn bằng phím
        self.hover_index = hover_index if hover_index is not None else selected_index  # Giữ nguyên trạng thái hover
        self.bg_x = 0  
        self.bg_speed = 100  

        # Tạo danh sách nút
        self.buttons = [
            Button("Play", WINDOW_WIDTH // 2 - 150, 250, 300, 70, BLACK, (0,0,255), menu_font),
            Button("Settings", WINDOW_WIDTH // 2 - 150, 330, 300, 70, BLACK, (0,0,255), menu_font),
            Button("Credits", WINDOW_WIDTH // 2 - 150, 410, 300, 70, BLACK, (0,0,255), menu_font),
            Button("Exit", WINDOW_WIDTH // 2 - 150, 490, 300, 70, BLACK, (0,0,255), menu_font)
        ]

    def draw(self):
        """Vẽ menu lên màn hình"""
        screen.fill(BGCOLOR)  
        if background:
            self.bg_x += self.bg_speed * (0.25 / FRAMERATE)
            if self.bg_x >= WINDOW_WIDTH:
                self.bg_x = 0
            screen.blit(background, (self.bg_x, 0))
            screen.blit(background, (self.bg_x - WINDOW_WIDTH, 0))

        # Tiêu đề game với hiệu ứng phát sáng
        draw_glow_text("SPACE RUNNER", title_font, (0,0,128), WINDOW_WIDTH // 2 - 445, 80)

        # Hiển thị các nút
        for i, button in enumerate(self.buttons):
            is_selected = (i == self.selected_index) or (i == self.hover_index)
            text_color = button.hover_color if is_selected else button.base_color
            button.draw(screen, text_color)

        pygame.display.flip()

    def run(self):
        """Vòng lặp main menu"""
        running = True
        while running:
            self.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return "exit", self.selected_index, self.hover_index  # Trả về cả hover

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        self.selected_index = (self.selected_index + 1) % len(self.buttons)
                        self.hover_index = self.selected_index  # Cập nhật hover khi di chuyển
                    elif event.key == pygame.K_UP:
                        self.selected_index = (self.selected_index - 1) % len(self.buttons)
                        self.hover_index = self.selected_index 
                    elif event.key == pygame.K_RETURN:
                        return ["play", "settings", "credits", "exit"][self.selected_index], self.selected_index, self.hover_index  # Trả về hover

                elif event.type == pygame.MOUSEMOTION:
                    for i, button in enumerate(self.buttons):
                        if button.rect.collidepoint(event.pos):
                            self.hover_index = i  # Cập nhật hover theo chuột
                            self.selected_index = i  # Đồng bộ với selected_index

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for i, button in enumerate(self.buttons):
                        if button.is_clicked():
                            return ["play", "settings", "credits", "exit"][i], i, i
        return "menu", self.selected_index, self.hover_index  # Trả về trạng thái

# Lớp hiển thị credits
class CreditsScene:
    def __init__(self):
        # Dùng tuple
        self.credits = [
            ("Game Developed by ", "Team 24"), ("",""),
            ("Programmers", "Phan Duc Nhan\nVo Gia Kiet\nNguyen Hoang Lap\nTran Dinh Khanh Du"), ("",""),
            ("Special Thanks to ", "Python _ Pygame _ Tiled _ OpenGameArt")
        ]
    
    def draw(self):
        """Vẽ màn hình credits"""
        screen.fill(BGCOLOR)
        # Tiêu đề credits
        draw_glow_text("CREDITS", credit_font, (0, 0, 0), WINDOW_WIDTH // 2 - 200, 70)

        y_offset = 200 # Trục y để chỉnh khoảng cách các dòng
        header_font = pygame.font.Font('data/font/8-BIT WONDER.TTF', 30)
        content_font = pygame.font.Font('data/font/8-BIT WONDER.TTF', 20)

        for header, content in self.credits:
            header_surface = header_font.render(header, True, BUTTON_COLOR)
            screen.blit(header_surface, (WINDOW_WIDTH // 2 - header_surface.get_width() // 2 + 30, y_offset))
            y_offset += 40 # Dời xuống

            for line in content.split("\n"):
                content_surface = content_font.render(line, True, WHITE)
                screen.blit(content_surface, (WINDOW_WIDTH // 2 - content_surface.get_width() // 2 + 30, y_offset))
                y_offset += 20 # Giãn cách giữa các dòng nội dung

            y_offset += 5 # Tạo khoảng cách giữa từng nhóm thông tin

        # Phần ESC để quay lại menu
        return_font = pygame.font.Font('data/font/8-BIT WONDER.TTF', 35)
        text_surface = return_font.render("Press ESC to return", True, BUTTON_COLOR)
        screen.blit(text_surface, (WINDOW_WIDTH // 2 - text_surface.get_width() // 2 + 30, WINDOW_HEIGHT - 80))
        pygame.display.flip()

    def run(self):
        """Vòng lặp màn hình credits"""
        running = True
        while running:
            self.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return "exit"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "menu"

# Chạy thử menu
# if __name__ == "__main__":
#     menu = GameMenu()
#     while True:
#         action = menu.run()
#         if action == "credits":
#             CreditsScene().run()
#         elif action == "exit":
#             break
