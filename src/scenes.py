import pygame  
from settings import *
from support import *

# Khởi tạo pygame
pygame.init()

# Khởi tạo màn hình
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
screen_rect = screen.get_rect()
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

# Khởi tạo biến toàn cục để xử lý lưu trạng thái ON/OFF của MainSettings
game_settings = {
    "MUSIC": "ON",
    "SOUND EFFECTS": "ON"
}

# Hàm vẽ chữ phát sáng neon (Glow effect)
"""
text: Chuỗi văn bản cần hiển thị.
font: Đối tượng font của Pygame (pygame.font.Font) để hiển thị văn bản.
color: Màu chính của văn bản dưới dạng bộ 3 giá trị RGB (ví dụ: (255, 0, 0) cho màu đỏ).
x, y: Tọa độ hiển thị văn bản trên màn hình.
"""
def draw_glow_text(text, font, color, x, y):
    # Ví dụ: Nếu màu gốc là (100, 100, 100), thì màu glow sẽ là (150, 150, 150).
    glow_color = (min(color[0] + 50, 255), min(color[1] + 50, 255), min(color[2] + 50, 255))  # Giới hạn max 255
    # Vẽ hiệu ứng glow bằng cách vẽ nhiều lớp xung quanh chữ
    # minh họa:
    # (x-3, y-3)   (x, y-3)   (x+3, y-3)
    # (x-3, y)     (x, y)     (x+3, y)
    # (x-3, y+3)   (x, y+3)   (x+3, y+3)
    for dx in range(-3, 4):
        for dy in range(-3, 4):
            glow_text = font.render(text, True, glow_color)
            screen.blit(glow_text, (x + dx, y + dy))
    #  Vẽ chữ chính (màu thật) lên trên cùng
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
        self.rect = pygame.Rect(x, y, width, height) # tạo vùng nhấn 
    
    # Hàm vẽ nút lên màn hình
    def draw(self, screen, text_color):
        """Vẽ nút với màu chữ thay đổi"""
        text_surface = self.font.render(self.text, True, text_color) # Tạo bề mặt văn bản (text surface) với nội dung self.text, màu text_color
        text_rect = text_surface.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2)) # tạo hcn + căn giữa văn bản vào nút
        screen.blit(text_surface, text_rect) # Vẽ chữ lên màn hình tại vị trí text_rect

    # Kiểm tra xem nút có bị nhấn không
    def is_clicked(self):
        """Kiểm tra xem nút có bị click hay không"""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        return self.rect.collidepoint(mouse_x, mouse_y) #Kiểm tra xem tọa độ chuột có nằm trong hình chữ nhật self.rect không.

import pygame

class TransitionScene:
    def __init__(self, screen, duration=500):
        """Tạo hiệu ứng chuyển cảnh kèm màn hình Loading"""
        self.screen = screen
        self.duration = duration  # Thời gian fade (ms)
        self.clock = pygame.time.Clock()

        # Load font từ thư mục dự án
        self.loading_font = pygame.font.Font("data/font/8-BIT WONDER.TTF", 30)  # Font Loading

    def fade(self, direction="out"):
        """Thực hiện hiệu ứng fade-in hoặc fade-out"""
        fade_surface = pygame.Surface(self.screen.get_size())
        fade_surface.fill((0, 0, 0))

        step = 10  # Bước alpha (mượt hơn)
        alpha_range = range(0, 256, step) if direction == "out" else range(255, -1, -step)

        for alpha in alpha_range:
            fade_surface.set_alpha(alpha)
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.update()
            self.clock.tick(100)

    def draw_loading_screen(self):
        """Vẽ màn hình Loading trước khi fade-in"""
        self.screen.fill((0, 0, 0))  # Nền đen
        loading_text = self.loading_font.render("* Loading", True, (200, 200, 200))
        self.screen.blit(loading_text, (20, 10))  # Hiển thị Loading ở góc trái trên cùng
        pygame.display.update()  # Cập nhật màn hình ngay

    def fade_out_in_with_loading(self):
        """Chuyển cảnh với hiệu ứng mờ dần + màn hình Loading"""
        self.fade("out")  # Fade-out trước
        self.draw_loading_screen()  # Hiển thị màn hình Loading ngay khi tối hoàn toàn
        pygame.time.delay(1500)  # Chờ 1.5s để Loading
        self.fade("in")  # Fade-in để vào màn hình tiếp theo


# Màn hình chính
class GameMenu:
    def __init__(self, selected_index=0, hover_index=0):
        self.transition = TransitionScene(screen)
        self.selected_index = selected_index  # Chỉ số nút được chọn bằng phím (trạng thái)
        self.hover_index = hover_index if hover_index is not None else selected_index  # Giữ nguyên trạng thái hover (màu)
        # Thiết lập hình nền trượt
        self.bg_x = 0  # Vị trí hiện tại của nền3
        self.bg_speed = 100 # Tốc độ di chuyển của nền
        self.background = background

        # Tạo danh sách nút, font chữ màu xanh dương khi chuột hover lên
        self.buttons = [
            Button("Play", WINDOW_WIDTH // 2 - 167, 250, 320, 70, BLACK, (0,0,255), menu_font),
            Button("Settings", WINDOW_WIDTH // 2 - 167, 330, 320, 70, BLACK, (0,0,255), menu_font),
            Button("Credits", WINDOW_WIDTH // 2 - 167, 410, 320, 70, BLACK, (0,0,255), menu_font),
            Button("Exit", WINDOW_WIDTH // 2 - 167, 490, 320, 70, BLACK, (0,0,255), menu_font)
        ]

    def draw(self):
        """Vẽ menu lên màn hình"""
        # screen.fill(BGCOLOR)  
        if background:
            # Cập nhật vị trí nền game
            self.bg_x += self.bg_speed * (0.5 / FRAMERATE)
            if self.bg_x >= WINDOW_WIDTH:
                self.bg_x = 0
            screen.blit(self.background, (self.bg_x, 0))
            screen.blit(self.background, (self.bg_x - WINDOW_WIDTH, 0))

        # Vẽ khung bo tròn cho tiêu đề game
        title_x, title_y, title_w, title_h = WINDOW_WIDTH // 2 - 477, 65, 970, 120
        pygame.draw.rect(screen, (0, 0, 120), (title_x, title_y, title_w, title_h), border_radius=25)  # Khung bo tròn
        # Tiêu đề game màu xanh đậm với hiệu ứng phát sáng
        draw_glow_text("SPACE RUNNER", title_font, (0,0,200), WINDOW_WIDTH // 2 - 445, 80)

        # Hiển thị các nút
        """
        Nếu nút đang được hover hoặc chọn bằng phím, nó sẽ hiển thị màu hover.
        Nếu không, nó hiển thị màu mặc định.
        """
        for i, button in enumerate(self.buttons):
            is_selected = (i == self.selected_index) or (i == self.hover_index)
            text_color = button.hover_color if is_selected else button.base_color

            # Vẽ khung bo tròn xung quanh nút
            # button_x, button_y, button_w, button_h = button.x, button.y, button.width, button.height
            # rect_color = (0, 20, 150) if is_selected else (0, 20, 170)  # Màu khác khi hover
            # pygame.draw.rect(screen, rect_color, (button_x, button_y, button_w, button_h), border_radius=15)
            
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
                
                # Xử lý điều hướng bằng bàn phím
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        self.selected_index = (self.selected_index + 1) % len(self.buttons)
                        self.hover_index = self.selected_index  # Cập nhật hover khi di chuyển
                    elif event.key == pygame.K_UP:
                        self.selected_index = (self.selected_index - 1) % len(self.buttons)
                        self.hover_index = self.selected_index 
                    elif event.key == pygame.K_RETURN:
                        selected_option = ["play", "settings", "credits", "exit"][self.selected_index]
                        
                        if selected_option == "exit":
                            pygame.quit()  # Thoát game ngay lập tức
                            return "exit", self.selected_index, self.hover_index  # Giữ 3 giá trị
                        elif selected_option == "play":
                            self.transition.fade_out_in_with_loading()  # Hiệu ứng chỉ áp dụng khi không phải "Exit"
                            return selected_option, self.selected_index, self.hover_index
                        else: 
                            return selected_option, self.selected_index, self.hover_index

                # Xử lý hover bằng chuột: Nếu chuột di chuyển vào nút, cập nhật hover_index và selected_index.
                elif event.type == pygame.MOUSEMOTION:
                    for i, button in enumerate(self.buttons):
                        if button.rect.collidepoint(event.pos):
                            self.hover_index = i  # Cập nhật hover theo chuột
                            self.selected_index = i  # Đồng bộ với selected_index

                # Xử lý click chuột: Nếu nhấn chuột vào nút, trả về màn hình tương ứng.
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for i, button in enumerate(self.buttons):
                        if button.is_clicked():
                            selected_option = ["play", "settings", "credits", "exit"][self.selected_index]
                        
                            if selected_option == "exit":
                                pygame.quit()  # Thoát game ngay lập tức
                                return "exit", self.selected_index, self.hover_index  # Giữ 3 giá trị
                            elif selected_option == "play":
                                self.transition.fade_out_in_with_loading()  # Hiệu ứng chỉ áp dụng khi không phải "Exit"
                                return selected_option, self.selected_index, self.hover_index
                            else:
                                return selected_option, self.selected_index, self.hover_index
        return "menu", self.selected_index, self.hover_index  # Trả về trạng thái

# Lớp hiển thị credits
class CreditsScene:
    def __init__(self):
        # Dùng tuple
        self.credits = [
            ("Game Developed by ", "Team 24"), ("",""),
            ("Programmers", "Phan Duc Nhan\nVo Gia Kiet\nNguyen Hoang Lap\nTran Dinh Khanh Du"), ("",""),
            ("Special Thanks to ", "Professor Le Tan Long")
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
                y_offset += 22 # Giãn cách giữa các dòng nội dung

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

class MainSettings:
    def __init__(self, background):
        global game_settings  # Dùng biến toàn cục
        self.settings = [("MUSIC", game_settings["MUSIC"]), ("SOUND EFFECTS", game_settings["SOUND EFFECTS"]), ("BACK", "")]
        self.selected_index = 0
        self.background_image = background
        # self.bg_x = bg_x
        # self.bg_speed = min(bg_speed, 0.5)  # Giữ tốc độ tối đa là 2 để tránh quá nhanh

    def draw(self):
        """Vẽ màn hình settings với nền đứng yên và overlay trong suốt"""
        screen.fill((0, 0, 128))  # Nền xanh đứng yên

        # Tạo overlay đen trong suốt
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 128, 150))  # Màu đen với độ trong suốt (alpha = 150)
        screen.blit(overlay, (0, 0))  # Vẽ overlay lên màn hình

        title_font = pygame.font.Font('data/font/8-BIT WONDER.TTF', 50)
        option_font = pygame.font.Font('data/font/8-BIT WONDER.TTF', 30)

        # Tiêu đề
        # draw_glow_text("SETTINGS", credit_font, (0, 0, 0), WINDOW_WIDTH // 2 - 250, 70)
        title_surface = title_font.render("SETTINGS", True, (255, 255, 255))
        screen.blit(title_surface, (WINDOW_WIDTH // 2 - title_surface.get_width() // 2, 85))

        y_offset = 200  # Vị trí bắt đầu của menu
        box_width = 600  # Chiều rộng khung
        box_height = 60  # Chiều cao khung
        box_x = WINDOW_WIDTH // 2 - box_width // 2  # Căn giữa

        for i, (setting, value) in enumerate(self.settings):
            # Màu nền và chữ
            bg_color = (50, 50, 150) if i == self.selected_index else (30, 30, 100)
            text_color = (255, 255, 255) if i == self.selected_index else (200, 200, 255)

            # Vẽ khung chữ nhật bo góc
            pygame.draw.rect(screen, bg_color, (box_x, y_offset, box_width, box_height), border_radius=10)
            pygame.draw.rect(screen, (255, 255, 255), (box_x, y_offset, box_width, box_height), 2, border_radius=10)

            # Vẽ chữ
            setting_surface = option_font.render(setting, True, text_color)
            screen.blit(setting_surface, (box_x + 20, y_offset + 15))  # Căn lề trái

            if value:
                value_surface = option_font.render(value, True, text_color)
                screen.blit(value_surface, (box_x + box_width - 100, y_offset + 15))  # Căn lề phải

            y_offset += 80  # Tăng khoảng cách giữa các dòng

        pygame.display.flip()

    def run(self):
        """Vòng lặp màn hình settings"""
        # Khai báo các thông số vị trí UI để dùng chung
        running = True
        box_x = WINDOW_WIDTH // 2 - 300
        box_width = 600
        box_height = 60
        spacing = 80  # Khoảng cách giữa các ô
        
        while running:
            self.draw()
            mouse_x, mouse_y = pygame.mouse.get_pos()  # Lấy vị trí chuột
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return "exit"

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        # Di chuyển lên trong danh sách settings
                        self.selected_index = (self.selected_index - 1) % len(self.settings)
                    elif event.key == pygame.K_DOWN:
                        # Di chuyển xuống trong danh sách settings
                        self.selected_index = (self.selected_index + 1) % len(self.settings)
                    elif event.key == pygame.K_RETURN:
                        # Xử lý khi nhấn Enter để chọn setting
                        selected_option = self.settings[self.selected_index][0]
                        # Nếu chọn MUSIC hoặc SOUND EFFECTS, bật/tắt ON-OFF
                        if selected_option in ["MUSIC", "SOUND EFFECTS"]:
                            new_value = "OFF" if self.settings[self.selected_index][1] == "ON" else "ON"
                            self.settings[self.selected_index] = (selected_option, new_value)
                            game_settings[selected_option] = new_value  # Lưu lại trạng thái
                        elif selected_option == "BACK":
                            return "menu"

                elif event.type == pygame.MOUSEMOTION:
                    # Kiểm tra khi chuột di chuyển để cập nhật hover
                    for i in range(len(self.settings)):
                        y_offset = 200 + i * spacing  # Vị trí Y của từng ô
                        if box_x <= mouse_x <= box_x + box_width and y_offset <= mouse_y <= y_offset + box_height:
                            self.selected_index = i
                            break  # Khi tìm thấy phần tử thi thoát vòng lặp

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Kiểm tra khi click chuột vào các ô
                    for i, (setting, value) in enumerate(self.settings):
                        y_offset = 200 + i * spacing  # Vị trí Y của từng ô
                        if box_x <= mouse_x <= box_x + box_width and y_offset <= mouse_y <= y_offset + box_height:
                            if setting in ["MUSIC", "SOUND EFFECTS"]:
                                # Đảo trạng thái ON/OFF khi click vào MUSIC hoặc SOUND EFFECTS
                                new_value = "OFF" if value == "ON" else "ON"
                                self.settings[i] = (setting, new_value)
                                game_settings[setting] = new_value  # Lưu trạng thái
                            elif setting == "BACK":
                                return "menu"
                        y_offset += 80  # Dịch xuống dòng tiếp theo

        return "settings"


# Chạy thử menu
# if __name__ == "__main__":
#     menu = GameMenu()
#     while True:
#         action = menu.run()
#         if action == "credits":
#             CreditsScene().run()
#         elif action == "exit":
#             break
