import pygame
import random

# Initialize Pygame
pygame.init()

# Colors (updated to grayscale)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_GRAY = (85, 85, 85)
LIGHT_GRAY = (170, 170, 170)

# Game dimensions
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SCREEN_WIDTH = BLOCK_SIZE * (GRID_WIDTH + 6)
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[1, 1, 1], [0, 1, 0]],
    [[1, 1, 1], [1, 0, 0]],
    [[1, 1, 1], [0, 0, 1]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 1], [1, 1, 0]]
]

COLORS = [DARK_GRAY, LIGHT_GRAY, WHITE, DARK_GRAY, LIGHT_GRAY, WHITE, DARK_GRAY]

class Tetromino:
    def __init__(self):
        self.shape = random.choice(SHAPES)
        self.color = COLORS[SHAPES.index(self.shape)]
        self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = list(zip(*self.shape[::-1]))

class TetrisGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris Clone")
        self.clock = pygame.time.Clock()
        self.fps = 59.73  # Game Boy's frame rate
        self.level = 1
        self.lines_cleared = 0
        self.frames_per_drop = self.get_frames_per_drop()
        self.frame_count = 0
        self.grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = Tetromino()
        self.game_over = False
        self.score = 0
        self.font = pygame.font.Font(None, 36)
        self.paused = False
        self.pause_font = pygame.font.Font(None, 48)
        self.border_color = WHITE
        self.border_width = 2
        self.fast_fall_speed = 0.05  # Time in seconds between each drop when accelerating
        self.next_piece = Tetromino()

    def get_frames_per_drop(self):
        if self.level <= 9:
            return 48 - (self.level - 1) * 5
        elif self.level <= 12:
            return 6
        elif self.level <= 15:
            return 5
        elif self.level <= 18:
            return 4
        elif self.level <= 28:
            return 3
        else:
            return 2

    def draw_grid(self):
        for y, row in enumerate(self.grid):
            for x, color in enumerate(row):
                pygame.draw.rect(self.screen, color, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)

    def draw_piece(self):
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, self.current_piece.color,
                                     ((self.current_piece.x + x) * BLOCK_SIZE,
                                      (self.current_piece.y + y) * BLOCK_SIZE,
                                      BLOCK_SIZE, BLOCK_SIZE), 0)

    def draw_score(self):
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (GRID_WIDTH * BLOCK_SIZE + 10, 10))

    def check_collision(self, dx=0, dy=0):
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x, new_y = self.current_piece.x + x + dx, self.current_piece.y + y + dy
                    if (new_x < 0 or new_x >= GRID_WIDTH or
                        new_y >= GRID_HEIGHT or
                        (new_y >= 0 and self.grid[new_y][new_x] != BLACK)):
                        return True
        return False

    def merge_piece(self):
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[self.current_piece.y + y][self.current_piece.x + x] = self.current_piece.color
        self.clear_lines()
        self.current_piece = Tetromino()
        if self.check_collision():
            self.game_over = True

    def clear_lines(self):
        full_lines = [i for i, row in enumerate(self.grid) if all(cell != BLACK for cell in row)]
        for line in full_lines:
            del self.grid[line]
            self.grid.insert(0, [BLACK for _ in range(GRID_WIDTH)])
        lines_cleared = len(full_lines)
        self.lines_cleared += lines_cleared
        self.score += lines_cleared ** 2 * 100 * self.level
        self.update_level()

    def update_level(self):
        old_level = self.level
        self.level = min(self.lines_cleared // 10 + 1, 29)
        if self.level != old_level:
            self.frames_per_drop = self.get_frames_per_drop()

    def get_fall_speed(self):
        return self.fall_speeds[min(self.level - 1, 11)]

    def draw_pause(self):
        if self.paused:
            pause_text = self.pause_font.render("PAUSED", True, WHITE)
            text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(pause_text, text_rect)

    def draw_border(self):
        pygame.draw.rect(self.screen, self.border_color, 
                         (0, 0, GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE), 
                         self.border_width)

    def new_piece(self):
        self.current_piece = self.next_piece
        self.next_piece = Tetromino()

    def draw_next_piece(self):
        next_piece_text = self.font.render("Next:", True, WHITE)
        self.screen.blit(next_piece_text, (GRID_WIDTH * BLOCK_SIZE + 10, 50))
        for y, row in enumerate(self.next_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, self.next_piece.color,
                                     (GRID_WIDTH * BLOCK_SIZE + 20 + x * BLOCK_SIZE,
                                      100 + y * BLOCK_SIZE,
                                      BLOCK_SIZE, BLOCK_SIZE), 0)

    def draw_level(self):
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (GRID_WIDTH * BLOCK_SIZE + 10, 200))

    def run(self):
        while not self.game_over:
            self.clock.tick(self.fps)
            self.frame_count += 1

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.paused = not self.paused
                    if not self.paused:
                        if event.key == pygame.K_LEFT and not self.check_collision(dx=-1):
                            self.current_piece.x -= 1
                        if event.key == pygame.K_RIGHT and not self.check_collision(dx=1):
                            self.current_piece.x += 1
                        if event.key == pygame.K_UP:
                            rotated = list(zip(*self.current_piece.shape[::-1]))
                            if not self.check_collision():
                                self.current_piece.shape = rotated

            if not self.paused:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_DOWN]:
                    current_frames_per_drop = 2  # Fast drop speed
                else:
                    current_frames_per_drop = self.frames_per_drop

                if self.frame_count >= current_frames_per_drop:
                    if not self.check_collision(dy=1):
                        self.current_piece.y += 1
                    else:
                        self.merge_piece()
                        self.new_piece()
                        if self.check_collision():
                            self.game_over = True
                    self.frame_count = 0

            self.screen.fill(BLACK)
            self.draw_grid()
            self.draw_piece()
            self.draw_score()
            self.draw_next_piece()
            self.draw_level()
            self.draw_border()  # Add this line
            if self.paused:
                self.draw_pause()
            pygame.display.flip()

        print(f"Game Over! Final Score: {self.score}")

if __name__ == "__main__":
    game = TetrisGame()
    game.run()
    pygame.quit()
