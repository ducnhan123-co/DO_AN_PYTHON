import pygame
from game import Game  # Import class Game từ game.py
from scenes import *  # Import các scenes 

def main():
    pygame.init()  # Khởi tạo pygame
    # Khởi tạo màn hình
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Menu Game")
    selected_index = 0  
    hover_index = 0  # Thêm biến lưu hover
    
    current_scene = "menu"  # Bắt đầu với menu

    while True:
        if current_scene == "menu":
            current_scene, selected_index, hover_index = MainMenu(selected_index, hover_index).run()  # Giữ hover

        elif current_scene == "play":
            pygame.mixer.stop()  # Dừng nhạc nền
            game = Game()  # Tạo đối tượng game
            game.run()  # Chạy game
            current_scene = "menu"  # Quay lại menu sau khi chơi xong

        elif current_scene == "settings":
            settings = MainSettings(MainMenu().background) # Hiển thị settings
            current_scene = settings.run()

        elif current_scene == "credits":
            credits = CreditsScene()  # Hiển thị màn hình credits
            current_scene = credits.run()  # Quay lại menu sau khi xem xong

        elif current_scene == "exit":
            print("Thoát game.")
            pygame.quit()  # Đóng cửa sổ pygame
            break  # Dừng chương trình

if __name__ == "__main__":
    main()
