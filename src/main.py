import pygame
from game import Game  # Import class Game từ game.py
from menu_game import *  # Import menu và màn hình credits

def main():
    pygame.init()  # Khởi tạo pygame
    selected_index = 0  
    hover_index = None  # Thêm biến lưu hover

    current_scene = "menu"  # Bắt đầu với menu

    while True:
        if current_scene == "menu":
            current_scene, selected_index, hover_index = GameMenu(selected_index, hover_index).run()  # Giữ hover

        elif current_scene == "play":
            pygame.mixer.stop()  # Dừng nhạc nền
            game = Game()  # Tạo đối tượng game
            game.run()  # Chạy game
            current_scene = "menu"  # Quay lại menu sau khi chơi xong

        elif current_scene == "settings":
            print("Chưa có cài đặt, cần thêm setting")
            current_scene = "menu"

        elif current_scene == "credits":
            credits = CreditsScene()  # Hiển thị màn hình credits
            current_scene = credits.run()  # Quay lại menu sau khi xem xong

        elif current_scene == "exit":
            print("Thoát game.")
            pygame.quit()  # Đóng cửa sổ pygame
            break  # Dừng chương trình

if __name__ == "__main__":
    main()
