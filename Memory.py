import pygame
import random
import sys
import os
import json

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 680
FONT_SIZE = 32

BACKGROUND_COLOR = (24, 24, 37)
TILE_COLOR = (49, 50, 68)
FLIPPED_COLOR = (137, 180, 250)
TEXT_COLOR = (24, 24, 37)
HUD_COLOR = (205, 214, 244)
ALERT_COLOR = (243, 139, 168)
SUCCESS_COLOR = (166, 227, 161)
BTN_COLOR = (88, 91, 112)
BTN_HOVER_COLOR = (147, 153, 178)
SECRET_BTN_COLOR = (203, 166, 247) # لون مميز للمستوى السري

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Helwan Memory Game - Ultimate Edition")

try:
    icon_paths = ["hel-memory.png", "/usr/share/pixmaps/hel-memory.png", "/usr/share/icons/hicolor/scalable/apps/hel-memory.png"]
    for path in icon_paths:
        if os.path.exists(path):
            icon_surface = pygame.image.load(path)
            pygame.display.set_icon(icon_surface)
            break
except:
    pass

font = pygame.font.Font(None, FONT_SIZE)
big_font = pygame.font.Font(None, 44)

DATA_DIR = os.path.expanduser("~/.local/share/helwan-memory")
SAVE_FILE = os.path.join(DATA_DIR, "game_data.json")

class MemoryGame:
    def __init__(self):
        self.state = "MENU"  # MENU, PLAYING, PAUSED, GAMEOVER, WIN, ABOUT, LEADERBOARD
        self.difficulty = "Normal"
        self.rows = 4
        self.cols = 4
        self.tile_size = 100
        self.grid = []
        self.flipped_tiles = []
        self.matched_tiles = []
        self.waiting_for_flip_back = False
        self.last_flip_time = None
        
        self.score = 0
        self.combo = 0
        self.max_time = 50
        self.time_left = 50
        self.start_ticks = 0
        self.paused_ticks = 0
        self.pause_start_time = 0
        self.flash_timer = 0
        
        # متغيرات تأثيرات الشاشة (Screen Shake)
        self.shake_timer = 0
        self.shake_offset_x = 0
        self.shake_offset_y = 0

        # بيانات اللعبة المحفوظة والتقدم
        self.game_data = self.load_game_data()

    def load_game_data(self):
        default_data = {
            "high_scores": {"Easy": 0, "Normal": 0, "Hard": 0, "Helwan Core": 0},
            "hard_unlocked": False
        }
        try:
            if os.path.exists(SAVE_FILE):
                with open(SAVE_FILE, "r") as f:
                    return json.load(f)
        except:
            pass
        return default_data

    def save_game_data(self):
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            with open(SAVE_FILE, "w") as f:
                json.dump(self.game_data, f)
        except:
            pass

    def set_difficulty(self, diff):
        self.difficulty = diff
        if diff == "Easy":
            self.rows = 2
            self.cols = 4
            self.max_time = 30
        elif diff == "Normal":
            self.rows = 4
            self.cols = 4
            self.max_time = 50
        elif diff == "Hard":
            self.rows = 4
            self.cols = 4
            self.max_time = 70
        elif diff == "Helwan Core":
            self.rows = 4
            self.cols = 6  # شبكة أطول وأقوى (24 كارت)
            self.max_time = 90

    def start_game(self):
        self.state = "PLAYING"
        self.flipped_tiles = []
        self.matched_tiles = []
        self.waiting_for_flip_back = False
        self.score = 0
        self.combo = 0
        self.time_left = self.max_time
        self.start_ticks = pygame.time.get_ticks()
        self.paused_ticks = 0
        self.create_grid()
        self.shuffle_tiles()

    def create_grid(self):
        total_tiles = self.rows * self.cols
        pairs = total_tiles // 2
        numbers = list(range(1, pairs + 1)) * 2
        random.shuffle(numbers)
        self.grid = [numbers[i * self.cols:(i + 1) * self.cols] for i in range(self.rows)]
        # حساب الحجم ديناميكياً ليناسب الشبكة حتى لو كانت 4x6
        self.tile_size = min(480 // self.cols, 400 // self.rows)

    def shuffle_tiles(self):
        flat_list = [num for row in self.grid for num in row]
        random.shuffle(flat_list)
        self.grid = [flat_list[i * self.cols:(i + 1) * self.cols] for i in range(self.rows)]

    def select_tile(self, row, col):
        if self.waiting_for_flip_back or (row, col) in self.flipped_tiles or (row, col) in self.matched_tiles:
            return
            
        self.flipped_tiles.append((row, col))
        if len(self.flipped_tiles) == 2:
            self.check_match()

    def check_match(self):
        r1, c1 = self.flipped_tiles[0]
        r2, c2 = self.flipped_tiles[1]
        if self.grid[r1][c1] == self.grid[r2][c2]:
            self.matched_tiles.extend([self.flipped_tiles[0], self.flipped_tiles[1]])
            self.flipped_tiles = []
            self.combo += 1
            self.score += 50 * self.combo
        else:
            self.waiting_for_flip_back = True
            self.last_flip_time = pygame.time.get_ticks()
            self.flash_timer = pygame.time.get_ticks()
            self.trigger_screen_shake()  # تفعيل اهتزاز الشاشة عند الخطأ
            self.combo = 0
            self.score = max(0, self.score - 15)

    def trigger_screen_shake(self):
        self.shake_timer = pygame.time.get_ticks()

    def update(self):
        if self.state != "PLAYING":
            return

        # تحديث تأثير الاتزاز (Screen Shake)
        if pygame.time.get_ticks() - self.shake_timer < 300:
            self.shake_offset_x = random.randint(-6, 6)
            self.shake_offset_y = random.randint(-6, 6)
        else:
            self.shake_offset_x = 0
            self.shake_offset_y = 0

        elapsed = (pygame.time.get_ticks() - self.start_ticks - self.paused_ticks) // 1000
        self.time_left = max(0, self.max_time - elapsed)
        
        if self.time_left == 0:
            self.state = "GAMEOVER"

        if self.waiting_for_flip_back:
            if pygame.time.get_ticks() - self.last_flip_time > 1000:
                self.flipped_tiles = []
                self.waiting_for_flip_back = False

        if len(self.matched_tiles) == self.rows * self.cols:
            self.score += self.time_left * 10
            
            # تحديث أعلى سكور للمستوى الحالي
            if self.score > self.game_data["high_scores"].get(self.difficulty, 0):
                self.game_data["high_scores"][self.difficulty] = self.score

            # فتح المستوى السري لو ختم الـ Hard
            if self.difficulty == "Hard":
                self.game_data["hard_unlocked"] = True

            self.save_game_data()
            self.state = "WIN"

    def draw(self):
        current_bg = BACKGROUND_COLOR
        if self.state == "PLAYING" and self.waiting_for_flip_back and pygame.time.get_ticks() - self.flash_timer < 250:
            current_bg = (60, 30, 40)

        # رسم الشاشة مع تطبيق الإزاحة للـ Screen Shake
        render_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        render_surface.fill(current_bg)

        if self.state == "MENU":
            title = big_font.render("HELWAN MEMORY", True, FLIPPED_COLOR)
            render_surface.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 70)))

            self.draw_button_on(render_surface, "Start - Easy (2x4) [30s]", 130, BTN_COLOR)
            self.draw_button_on(render_surface, "Start - Normal (4x4) [50s]", 195, BTN_COLOR)
            self.draw_button_on(render_surface, "Start - Hard (4x4) [70s]", 260, BTN_COLOR)
            
            # المستوى السري يظهر بلون مختلف لما يتفتح
            if self.game_data["hard_unlocked"]:
                self.draw_button_on(render_surface, "🔥 Helwan Core (Secret)", 325, SECRET_BTN_COLOR)
                lb_y, about_y, exit_y = 390, 455, 520
            else:
                lb_y, about_y, exit_y = 325, 390, 455

            self.draw_button_on(render_surface, "High Scores", lb_y, BTN_COLOR)
            self.draw_button_on(render_surface, "About", about_y, BTN_COLOR)
            self.draw_button_on(render_surface, "Exit", exit_y, BTN_COLOR)

        elif self.state == "LEADERBOARD":
            title = big_font.render("HIGH SCORES", True, FLIPPED_COLOR)
            render_surface.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 80)))

            y_pos = 180
            for diff, sc in self.game_data["high_scores"].items():
                txt = font.render(f"{diff}: {sc} pts", True, HUD_COLOR)
                render_surface.blit(txt, txt.get_rect(center=(SCREEN_WIDTH//2, y_pos)))
                y_pos += 60

            self.draw_button_on(render_surface, "Back to Menu", 510, BTN_COLOR)

        elif self.state == "ABOUT":
            title = big_font.render("ABOUT GAME", True, FLIPPED_COLOR)
            render_surface.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 80)))

            desc1 = font.render("Helwan Memory Game - Ultimate Edition", True, HUD_COLOR)
            desc2 = font.render("Developed & Adapted for Helwan Linux", True, SUCCESS_COLOR)
            desc3 = font.render("Features Screen Shake, Combos & Secret Core!", True, (180, 190, 210))
            
            render_surface.blit(desc1, desc1.get_rect(center=(SCREEN_WIDTH//2, 220)))
            render_surface.blit(desc2, desc2.get_rect(center=(SCREEN_WIDTH//2, 280)))
            render_surface.blit(desc3, desc3.get_rect(center=(SCREEN_WIDTH//2, 340)))

            self.draw_button_on(render_surface, "Back to Menu", 510, BTN_COLOR)

        elif self.state in ["PLAYING", "PAUSED"]:
            score_text = font.render(f"Score: {self.score}", True, HUD_COLOR)
            combo_text = font.render(f"Combo: x{self.combo}🔥", True, SUCCESS_COLOR if self.combo > 1 else HUD_COLOR)
            time_text = font.render(f"Time: {self.time_left}s", True, ALERT_COLOR if self.time_left < 15 else HUD_COLOR)
            
            render_surface.blit(score_text, (20, 20))
            render_surface.blit(combo_text, (200, 20))
            render_surface.blit(time_text, (460, 20))

            self.draw_action_button_on(render_surface, "Menu", 140, 65, 80, 32)
            self.draw_action_button_on(render_surface, "Pause" if self.state == "PLAYING" else "Resume", 370, 65, 90, 32)

            offset_y = 115
            grid_w = self.cols * self.tile_size
            offset_x = (SCREEN_WIDTH - grid_w) // 2
            
            for row in range(self.rows):
                for col in range(self.cols):
                    x = col * self.tile_size + offset_x
                    y = row * self.tile_size + offset_y
                    rect = pygame.Rect(x, y, self.tile_size - 6, self.tile_size - 6)
                    
                    if self.state == "PAUSED":
                        pygame.draw.rect(render_surface, TILE_COLOR, rect, border_radius=8)
                    elif (row, col) in self.flipped_tiles or (row, col) in self.matched_tiles:
                        pygame.draw.rect(render_surface, FLIPPED_COLOR, rect, border_radius=8)
                        text = font.render(str(self.grid[row][col]), True, TEXT_COLOR)
                        render_surface.blit(text, text.get_rect(center=rect.center))
                    else:
                        pygame.draw.rect(render_surface, TILE_COLOR, rect, border_radius=8)

                    pygame.draw.rect(render_surface, BACKGROUND_COLOR, rect, 3, border_radius=8)

            if self.state == "PAUSED":
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 160))
                render_surface.blit(overlay, (0, 0))
                pause_msg = big_font.render("GAME PAUSED", True, FLIPPED_COLOR)
                render_surface.blit(pause_msg, pause_msg.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))

        elif self.state in ["WIN", "GAMEOVER"]:
            msg = "VICTORY! 🔥" if self.state == "WIN" else "GAME OVER! 💀"
            col = SUCCESS_COLOR if self.state == "WIN" else ALERT_COLOR
            
            t = big_font.render(msg, True, col)
            s = font.render(f"Final Score: {self.score}", True, HUD_COLOR)
            r = font.render("Press ENTER to return to Menu", True, FLIPPED_COLOR)
            
            render_surface.blit(t, t.get_rect(center=(SCREEN_WIDTH//2, 220)))
            render_surface.blit(s, s.get_rect(center=(SCREEN_WIDTH//2, 290)))
            render_surface.blit(r, r.get_rect(center=(SCREEN_WIDTH//2, 370)))

        # رسم الشاشة الأصلية مضافاً إليها إزاحة الـ Shake
        screen.blit(render_surface, (self.shake_offset_x, self.shake_offset_y))

    def draw_button_on(self, surface, text, y_pos, bg_col):
        rect = pygame.Rect(150, y_pos, 300, 50)
        mouse_pos = pygame.mouse.get_pos()
        # تعديل الإحداثيات لو فيه Screen Shake بسيط
        adjusted_mouse = (mouse_pos[0] - self.shake_offset_x, mouse_pos[1] - self.shake_offset_y)
        is_hover = rect.collidepoint(adjusted_mouse)
        
        pygame.draw.rect(surface, BTN_HOVER_COLOR if is_hover else bg_col, rect, border_radius=10)
        t = font.render(text, True, (24, 24, 37) if bg_col == SECRET_BTN_COLOR else (255, 255, 255))
        surface.blit(t, t.get_rect(center=rect.center))

    def draw_action_button_on(self, surface, text, x_pos, y_pos, w, h):
        rect = pygame.Rect(x_pos, y_pos, w, h)
        mouse_pos = pygame.mouse.get_pos()
        adjusted_mouse = (mouse_pos[0] - self.shake_offset_x, mouse_pos[1] - self.shake_offset_y)
        is_hover = rect.collidepoint(adjusted_mouse)
        
        pygame.draw.rect(surface, BTN_HOVER_COLOR if is_hover else BTN_COLOR, rect, border_radius=6)
        font_small = pygame.font.Font(None, 22)
        t = font_small.render(text, True, (255, 255, 255))
        surface.blit(t, t.get_rect(center=rect.center))

    def handle_click(self, pos):
        # تكييف الماوس مع الـ Shake
        x = pos[0] - self.shake_offset_x
        y = pos[1] - self.shake_offset_y

        if self.state == "MENU":
            if 150 <= x <= 450:
                if 130 <= y <= 180:
                    self.set_difficulty("Easy")
                    self.start_game()
                elif 195 <= y <= 245:
                    self.set_difficulty("Normal")
                    self.start_game()
                elif 260 <= y <= 310:
                    self.set_difficulty("Hard")
                    self.start_game()
                
                # فحص الأزرار بناءً على حالة فتح المستوى السري
                if self.game_data["hard_unlocked"]:
                    if 325 <= y <= 375:
                        self.set_difficulty("Helwan Core")
                        self.start_game()
                    elif 390 <= y <= 440:
                        self.state = "LEADERBOARD"
                    elif 455 <= y <= 505:
                        self.state = "ABOUT"
                    elif 520 <= y <= 570:
                        pygame.quit()
                        sys.exit()
                else:
                    if 325 <= y <= 375:
                        self.state = "LEADERBOARD"
                    elif 390 <= y <= 440:
                        self.state = "ABOUT"
                    elif 455 <= y <= 505:
                        pygame.quit()
                        sys.exit()

        elif self.state in ["LEADERBOARD", "ABOUT"]:
            if 150 <= x <= 450 and 510 <= y <= 560:
                self.state = "MENU"

        elif self.state in ["PLAYING", "PAUSED"]:
            if 140 <= x <= 220 and 65 <= y <= 97:
                self.state = "MENU"
                return
            if 370 <= x <= 460 and 65 <= y <= 97:
                if self.state == "PLAYING":
                    self.state = "PAUSED"
                    self.pause_start_time = pygame.time.get_ticks()
                elif self.state == "PAUSED":
                    self.state = "PLAYING"
                    self.paused_ticks += pygame.time.get_ticks() - self.pause_start_time
                return

            if self.state == "PLAYING":
                offset_y = 115
                grid_w = self.cols * self.tile_size
                offset_x = (SCREEN_WIDTH - grid_w) // 2
                
                if y >= offset_y:
                    row = (y - offset_y) // self.tile_size
                    col = (x - offset_x) // self.tile_size
                    if 0 <= row < self.rows and 0 <= col < self.cols:
                        self.select_tile(row, col)

def main():
    game = MemoryGame()
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                game.handle_click(pygame.mouse.get_pos())
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and game.state in ["WIN", "GAMEOVER"]:
                    game.state = "MENU"

        game.update()
        game.draw()
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
