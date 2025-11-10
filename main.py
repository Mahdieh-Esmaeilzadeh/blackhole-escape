import pygame
import random
import math
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Escape Black Hole! with Asteroids!")
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
PURPLE = (138, 43, 226)
ORANGE = (255, 150, 0)
GREEN = (0, 255, 0)
BLUE = (100, 150, 255)
DARK_PURPLE = (75, 0, 130)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

# Game variables
player_size = 25
player_speed = 7  # Player speed (adjust here!)
base_pull_constant = 600  # Weaker gravity for better control
hole_radius = 55
win_distance = 120  # Distance to win
win_y_threshold = 100  # y < this = near top
alignment_threshold = 50  # X distance for "alignment" (vertical lock)
asteroid_spawn_rate = 0.02  # Asteroid spawn chance per frame
bullet_speed = 12  # Bullet speed
shoot_cooldown = 200  # ms between shots

font = pygame.font.SysFont("Arial", 28, bold=True)  # Slightly smaller font
big_font = pygame.font.SysFont("Arial", 80, bold=True)
small_font = pygame.font.SysFont("Arial", 20)  # Smaller for UI

class Particle:
    def __init__(self, x, y, vx, vy, color, life=30):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.life = life
        self.max_life = life
    
    def update(self, dt):
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        self.life -= 1
        self.vx *= 0.98
        self.vy *= 0.98
    
    def draw(self, screen):
        alpha = int(255 * self.life / self.max_life)
        size = int(3 * self.life / self.max_life) + 1
        s = pygame.Surface((size*4, size*4), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color[:3], alpha), (size*2, size*2), size)
        screen.blit(s, (self.x - size*2, self.y - size*2))
    
    def alive(self):
        return self.life > 0

class Asteroid:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = -30  # Start from top
        self.size = random.randint(15, 30)
        self.speed = random.uniform(2, 5)
        self.vx = random.uniform(-1, 1)  # Slow horizontal drift
    
    def update(self, dt):
        self.y += self.speed * 60 * dt
        self.x += self.vx * 60 * dt
        if self.y > HEIGHT + 50:
            return True  # Remove if off screen
        return False
    
    def draw(self, screen):
        # Simple gray circle
        pygame.draw.circle(screen, GRAY, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(screen, DARK_GRAY, (int(self.x), int(self.y)), self.size, 2)
    
    def collides_with(self, other_x, other_y, other_size):
        dx = self.x - other_x
        dy = self.y - other_y
        dist = math.hypot(dx, dy)
        return dist < self.size + other_size

class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 4
    
    def update(self, dt):
        self.y -= bullet_speed * 60 * dt
        return self.y < -10  # Remove if off screen
    
    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.size)

def reset_game():
    global player_x, player_y, hole_x, hole_y, hole_speed_x, hole_speed_y, score, game_over, win, particles, best_score, asteroids, bullets, last_shot_time
    player_x = WIDTH // 2
    player_y = HEIGHT - 100  # Start from bottom
    hole_x = WIDTH // 2
    hole_y = HEIGHT // 2 + 50
    hole_speed_x = random.choice([-1, 1]) * random.uniform(0.3, 0.8)
    hole_speed_y = random.choice([-1, 1]) * random.uniform(0.3, 0.8)
    score = 0
    game_over = False
    win = False
    particles = []
    asteroids = []
    bullets = []
    last_shot_time = 0

# Lists
stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(0.3, 1.8)) for _ in range(200)]
particles = []
asteroids = []
bullets = []
best_score = 0

reset_game()
running = True

while running:
    dt = clock.tick(60) / 1000.0
    screen.fill(BLACK)

    # Moving stars with layers
    for i, (x, y, speed) in enumerate(stars):
        y += speed * 80 * dt
        if y > HEIGHT:
            y -= HEIGHT
            x = random.randint(0, WIDTH)
        stars[i] = (x, y, speed)
        size = 1 if speed < 1 else 2
        color_intensity = int(255 * (1 - speed / 2))
        pygame.draw.circle(screen, (color_intensity, color_intensity, 255), (int(x), int(y)), size)

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if (game_over or win) and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reset_game()
            if event.key == pygame.K_q:
                running = False
        if not game_over and not win and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                current_time = pygame.time.get_ticks()
                if current_time - last_shot_time > shoot_cooldown:
                    bullets.append(Bullet(player_x, player_y))
                    last_shot_time = current_time

    if not game_over and not win:
        # Check alignment for vertical movement
        dx = abs(player_x - hole_x)
        can_move_vertical = dx < alignment_threshold

        # Player controls (vertical only if aligned)
        keys = pygame.key.get_pressed()
        move_x = 0
        move_y = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move_x -= player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move_x += player_speed
        if can_move_vertical:
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                move_y -= player_speed  # Up!
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                move_y += player_speed  # Down
        
        player_x += move_x * 60 * dt
        player_y += move_y * 60 * dt
        
        # Clamp player to screen
        player_x = max(player_size, min(WIDTH - player_size, player_x))
        player_y = max(player_size, min(HEIGHT - player_size, player_y))

        # Black hole movement (faster!)
        hole_x += hole_speed_x * 80 * dt
        hole_y += hole_speed_y * 80 * dt
        if hole_x < hole_radius + 20 or hole_x > WIDTH - hole_radius - 20:
            hole_speed_x *= -1
        if hole_y < hole_radius + 20 or hole_y > HEIGHT - hole_radius - 20:
            hole_speed_y *= -1

        # Gravity
        dx_grav = hole_x - player_x
        dy_grav = hole_y - player_y
        distance = math.hypot(dx_grav, dy_grav)
        if distance < 12:
            distance = 12

        pull_strength = base_pull_constant / (distance ** 2)
        pull_x = (dx_grav / distance) * pull_strength * dt
        pull_y = (dy_grav / distance) * pull_strength * dt
        player_x += pull_x
        player_y += pull_y

        # Spawn asteroids
        if random.random() < asteroid_spawn_rate:
            asteroids.append(Asteroid())

        # Update asteroids
        asteroids = [a for a in asteroids if not a.update(dt)]
        for asteroid in asteroids:
            if asteroid.collides_with(player_x, player_y, player_size):
                game_over = True
                best_score = max(best_score, score)

        # Update bullets
        for bullet in bullets[:]:
            if bullet.update(dt):
                bullets.remove(bullet)
            else:
                for asteroid in asteroids[:]:
                    if asteroid.collides_with(bullet.x, bullet.y, bullet.size):
                        # Destroy asteroid + bonus score
                        asteroids.remove(asteroid)
                        bullets.remove(bullet)
                        score += 100  # Bonus for destroy
                        # Explosion particles
                        for _ in range(10):
                            vx = random.uniform(-5, 5)
                            vy = random.uniform(-5, 5)
                            particles.append(Particle(asteroid.x, asteroid.y, vx, vy, ORANGE, 20))
                        break

        # Check win/lose
        if distance < hole_radius + player_size:
            game_over = True
            best_score = max(best_score, score)
        elif distance > win_distance and player_y < win_y_threshold:  # Escape up!
            win = True
            best_score = max(best_score, score)
        else:
            score += int(60 * dt)

        # Engine particles (based on movement)
        if abs(move_x) > 0 or abs(move_y) > 0 or abs(pull_x) > 0.1 or abs(pull_y) > 0.1:
            for _ in range(3):
                vx = random.uniform(-2, 2) + (move_x / player_speed) * 1
                vy = random.uniform(3, 8) + (move_y / player_speed) * 1
                particles.append(Particle(player_x, player_y + player_size, vx, vy, (255, 100 + random.randint(0,50), 0)))

    # Update particles
    particles = [p for p in particles if p.alive()]
    for p in particles:
        p.update(dt)
        p.draw(screen)

    # Draw asteroids
    for asteroid in asteroids:
        asteroid.draw(screen)

    # Draw bullets
    for bullet in bullets:
        bullet.draw(screen)

    # Black hole with effects (rotating rings + distortion)
    for i in range(8):
        r = hole_radius + i * 15
        alpha = max(0, 200 - i * 25)
        thickness = max(1, 6 - i)
        color = (*DARK_PURPLE, alpha)
        s = pygame.Surface((r*2*2, r*2*2), pygame.SRCALPHA)
        pygame.draw.circle(s, color, (r*2, r*2), r, thickness)
        rotated = pygame.transform.rotate(s, i * 5 - pygame.time.get_ticks() * 0.1)
        screen.blit(rotated, (hole_x - rotated.get_width()//2, hole_y - rotated.get_height()//2))
    
    pygame.draw.circle(screen, BLACK, (int(hole_x), int(hole_y)), hole_radius)
    pygame.draw.circle(screen, PURPLE, (int(hole_x), int(hole_y)), hole_radius, 5)
    pygame.draw.circle(screen, RED, (int(hole_x), int(hole_y)), hole_radius // 4)

    # Player ship with shadow and details
    shadow = (int(player_x + 3), int(player_y + 3))
    pygame.draw.polygon(screen, (50, 50, 50), [
        (shadow[0], shadow[1] - player_size),
        (shadow[0] - player_size, shadow[1] + player_size),
        (shadow[0] + player_size, shadow[1] + player_size)
    ])
    pygame.draw.polygon(screen, YELLOW, [
        (player_x, player_y - player_size),
        (player_x - player_size//1.5, player_y + player_size//2),
        (player_x + player_size//1.5, player_y + player_size//2)
    ])
    pygame.draw.polygon(screen, ORANGE, [
        (player_x, player_y - player_size//2),
        (player_x - player_size//2, player_y + player_size//2),
        (player_x + player_size//2, player_y + player_size//2)
    ])

    # Compact UI (top-left, smaller)
    score_text = small_font.render(f"Score: {int(score)}", True, WHITE)
    screen.blit(score_text, (10, 10))
    best_text = small_font.render(f"Best: {best_score}", True, YELLOW)
    screen.blit(best_text, (10, 30))
    
    # Compact controls hint (bottom-left)
    control_text = small_font.render("A/D: L/R | W/S: U/D (align) | SPACE: Shoot", True, BLUE)
    screen.blit(control_text, (10, HEIGHT - 40))
    
    # Compact alignment indicator
    align_color = GREEN if can_move_vertical else RED
    align_text = small_font.render(f"Align: {'Y' if can_move_vertical else 'N'} (X: {int(dx)})", True, align_color)
    screen.blit(align_text, (10, HEIGHT - 20))

    # Game Over screen
    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((20, 0, 40))
        screen.blit(overlay, (0, 0))
        
        game_over_text = big_font.render("Sucked In or Hit!", True, RED)
        restart_text = small_font.render("R: Restart | Q: Quit", True, WHITE)
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 60))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2))
        screen.blit(best_text, (WIDTH//2 - best_text.get_width()//2, HEIGHT//2 + 40))

    # Win screen (fireworks!)
    if win:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 20, 50))
        screen.blit(overlay, (0, 0))
        
        # Fireworks
        for _ in range(10):
            if random.random() < 0.5:
                px = random.randint(0, WIDTH)
                py = random.randint(0, HEIGHT//2)
                color = random.choice([YELLOW, RED, GREEN, ORANGE, BLUE])
                particles.append(Particle(px, py, random.uniform(-200,200)*dt, random.uniform(-400,0)*dt, color, 60))
        
        win_text = big_font.render("Escaped!", True, GREEN)
        score_win_text = small_font.render(f"Score: {int(score)}", True, YELLOW)
        restart_text = small_font.render("R: Restart | Q: Quit", True, WHITE)
        screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2 - 60))
        screen.blit(score_win_text, (WIDTH//2 - score_win_text.get_width()//2, HEIGHT//2))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 40))

    pygame.display.flip()

pygame.quit()
sys.exit()
