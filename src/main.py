import pygame
from game import Game  # Import class Game từ game.py
from scenes import *  # Import các scenes 

def main():
    # pygame.init()  # Khởi tạo pygame
    # Khởi tạo màn hình
    # global screen 
    # screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    # pygame.display.set_caption("Menu Game")
    selected_index = 0  
    hover_index = 0  # Thêm biến lưu hover
    title_font = pygame.font.Font(None, 72)  # Font mặc định, kích thước 72
    
    current_scene = "menu"  # Bắt đầu với menu

    while True:
        if current_scene == "menu":
            current_scene, selected_index, hover_index = MainMenu(screen,selected_index, hover_index).run()  # Giữ hover

        elif current_scene == "play":
            pygame.mixer.stop()  # Dừng nhạc nền
            game = Game()  # Tạo đối tượng game
            current_scene = game.run()  # Chạy game
              # Quay lại menu sau khi chơi xong

        elif current_scene == "settings":
            settings = MainSettings(screen, selected_index, hover_index) # Hiển thị settings
            current_scene = settings.run()

        elif current_scene == "credits":
            credits = CreditsScene(screen)  # Hiển thị màn hình credits
            current_scene = credits.run()  # Quay lại menu sau khi xem xong

        elif current_scene == "exit":
            print("Thoát game.")
            pygame.quit()  # Đóng cửa sổ pygame
            break  # Dừng chương trình

if __name__ == "__main__":
    main()