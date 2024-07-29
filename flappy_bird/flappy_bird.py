import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
PIPE_COLOR = (54, 155, 28)
BLACK = (0, 0, 0)


# Game class to encapsulate the game logic
class FlappyBirdGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Flappy Bird")
        self.clock = pygame.time.Clock()
        self.bird = Bird(50, 300)
        self.pipes = []
        self.score = 0
        self.running = True
        self.pipe_timer = 0
        self.pipe_interval = 1500
        self.font = pygame.font.SysFont(None, 48)

    def create_pipe(self):
        height = random.randint(150, 400)
        top_pipe = Pipe(SCREEN_WIDTH, 0, height)
        bottom_pipe = Pipe(SCREEN_WIDTH, height + 200, SCREEN_HEIGHT - height - 200)
        self.pipes.append((top_pipe, bottom_pipe))

    def draw(self):
        self.screen.fill(WHITE)
        self.bird.draw(self.screen)
        for top_pipe, bottom_pipe in self.pipes:
            top_pipe.draw(self.screen)
            bottom_pipe.draw(self.screen)
        self.display_score()
        pygame.display.update()
    
    def display_score(self):
        score_surface = self.font.render(str(self.score), True, BLACK)
        self.screen.blit(score_surface, (10, 10))

    def update(self):
        self.bird.update()
        for top_pipe, bottom_pipe in self.pipes:
            top_pipe.update()
            bottom_pipe.update()

        # Remove pipes that have moved out of the screen
        self.pipes = [(top_pipe, bottom_pipe) for top_pipe, bottom_pipe in self.pipes if
                      top_pipe.x + top_pipe.width > 0]

        # Check for collision
        for top_pipe, bottom_pipe in self.pipes:
            if self.bird.rect.colliderect(top_pipe.rect) or self.bird.rect.colliderect(bottom_pipe.rect):
                self.running = False

        # Check if bird is out of screen
        if self.bird.y + self.bird.height > SCREEN_HEIGHT or self.bird.y < 0:
            self.running = False
        
        for top_pipe, bottom_pipe in self.pipes:
            if top_pipe.x + top_pipe.width < self.bird.x and not top_pipe.passed:
                top_pipe.passed = True
                self.score += 1

    def run(self):
        self.create_pipe()  # Initial pipe
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.bird.flap()

            # Add new pipes at regular intervals
            self.pipe_timer += self.clock.get_time()
            if self.pipe_timer > self.pipe_interval:
                self.create_pipe()
                self.pipe_timer = 0

            self.update()
            self.draw()
            self.clock.tick(30)

        print("Game Over! Your score:", self.score)
        pygame.quit()


# Bird class to handle bird properties and actions
class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 34
        self.height = 24
        self.velocity = 0
        self.gravity = 0.5
        self.image = pygame.transform.scale(pygame.image.load("bird.jpg"), (self.width, self.height))
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def flap(self):
        self.velocity = -8

    def update(self):
        self.velocity += self.gravity
        self.y += self.velocity
        self.rect.y = self.y

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))


# Pipe class to handle pipe properties and actions
class Pipe:
    def __init__(self, x, y, height):
        self.x = x
        self.y = y
        self.width = 80
        self.height = height
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.color = PIPE_COLOR
        self.speed = 5
        self.passed = False

    def update(self):
        self.x -= self.speed
        self.rect.x = self.x

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)


if __name__ == "__main__":
    game = FlappyBirdGame()
    game.run()
