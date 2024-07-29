import random
import pygame

class Player:
    def __init__(self, x, y, image_path):
        self.x = x
        self.y = y
        self.y_speed = 0
        self.flying = False
        self.gravity = 0.3
        self.image = pygame.transform.scale(pygame.image.load(image_path), (60, 60))

    def update(self):
        if self.flying:
            self.y_speed += self.gravity
        else:
            self.y_speed -= self.gravity
        self.y -= self.y_speed

    def draw(self, screen):
        player_circle = pygame.draw.circle(screen, 'black', (self.x, self.y), 20)
        screen.blit(self.image, (self.x - 40, self.y - 30))
        return player_circle

    def reset(self, y):
        self.y = y
        self.y_speed = 0
        self.flying = False


class ObstacleMap:
    def __init__(self, screen_width, screen_height, rect_width, spacer, map_speed):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.rect_width = rect_width
        self.spacer = spacer
        self.map_speed = map_speed
        self.rects = []
        self.total_rects = screen_width // rect_width

    def generate_new(self):
        self.rects = []
        top_height = random.randint(0, 300)
        for i in range(self.total_rects):
            top_height = random.randint(top_height - self.spacer, top_height + self.spacer)
            if top_height < 0:
                top_height = 0
            elif top_height > 300:
                top_height = 300
            top_rect = pygame.Rect(i * self.rect_width, 0, self.rect_width, top_height)
            bot_rect = pygame.Rect(i * self.rect_width, top_height + 300, self.rect_width, self.screen_height)
            self.rects.append(top_rect)
            self.rects.append(bot_rect)
        return self.rects[0].bottom + 150

    def update(self, score):
        for rect in self.rects:
            rect.x -= self.map_speed
        if self.rects[0].x + self.rect_width < 0:
            self.rects.pop(0)
            self.rects.pop(0)
            top_height = random.randint(self.rects[-2].height - self.spacer, self.rects[-2].height + self.spacer)
            if top_height < 0:
                top_height = 0
            elif top_height > 300:
                top_height = 300
            new_top_rect = pygame.Rect(self.rects[-2].x + self.rect_width, 0, self.rect_width, top_height)
            new_bot_rect = pygame.Rect(self.rects[-2].x + self.rect_width, top_height + 300, self.rect_width, self.screen_height)
            self.rects.append(new_top_rect)
            self.rects.append(new_bot_rect)
            score += 1
        return score

    def draw(self, screen):
        for rect in self.rects:
            pygame.draw.rect(screen, 'green', rect)
        pygame.draw.rect(screen, 'dark gray', [0, 0, self.screen_width, self.screen_height], 12)

    def check_collision(self, player_circle):
        for rect in self.rects:
            if player_circle.colliderect(rect):
                return True
        return False


class HelicopterGame:
    def __init__(self, screen_width=1000, screen_height=600, fps=60):
        pygame.init()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode([screen_width, screen_height])
        pygame.display.set_caption('Helicopter in Python!')
        self.font = pygame.font.Font('freesansbold.ttf', 20)
        self.fps = fps
        self.timer = pygame.time.Clock()
        self.running = True

        self.player = Player(100, 300, 'helicopter.png')
        self.obstacle_map = ObstacleMap(screen_width, screen_height, 10, 10, 2)
        self.score = 0
        self.high_score = 0
        self.active = True
        self.new_map = True

    def run(self):
        while self.running:
            self.screen.fill('black')
            self.timer.tick(self.fps)
            if self.new_map:
                player_start_y = self.obstacle_map.generate_new()
                self.player.reset(player_start_y)
                self.new_map = False

            self.obstacle_map.draw(self.screen)
            player_circle = self.player.draw(self.screen)
            if self.active:
                self.player.update()
                self.score = self.obstacle_map.update(self.score)
            self.active = not self.obstacle_map.check_collision(player_circle)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.player.flying = True
                    if event.key == pygame.K_RETURN:
                        if not self.active:
                            self.new_map = True
                            self.active = True
                            if self.score > self.high_score:
                                self.high_score = self.score
                            self.score = 0
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        self.player.flying = False

            self.obstacle_map.map_speed = 2 + self.score // 50
            self.obstacle_map.spacer = 10 + self.score // 100

            self.screen.blit(self.font.render(f'Score: {self.score}', True, 'white'), (20, 15))
            self.screen.blit(self.font.render(f'High Score: {self.high_score}', True, 'white'), (20, 565))
            if not self.active:
                self.screen.blit(self.font.render('Press Enter to Restart', True, 'white'), (300, 15))
                self.screen.blit(self.font.render('Press Enter to Restart', True, 'white'), (300, 565))

            pygame.display.flip()
        pygame.quit()

if __name__ == "__main__":
    game = HelicopterGame()
    game.run()
