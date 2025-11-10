import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("فرار از سیاه‌چاله! 🚀")
clock = pygame.time.Clock()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
PURPLE = (138, 43, 226)
ORANGE = (255, 150, 0)

# متغیرهای بازی
player_size = 30
player_speed = 6
base_pull_constant = 800  # کاهش قدرت جاذبه برای کنترل بهتر

font = pygame.font.SysFont("Arial", 36)
big_font = pygame.font.SysFont("Arial", 72)

# تابع ریستارت بازی
def reset_game():
    global player_x, player_y, hole_x, hole_y, score, game_over, hole_speed_x, hole_speed_y
    player_x = WIDTH // 2
    player_y = HEIGHT - 100
    hole_x = WIDTH // 2
    hole_y = HEIGHT // 2
    hole_speed_x = random.choice([-1, 1]) * 0.5
    hole_speed_y = random.choice([-1, 1]) * 0.5
    score = 0
    game_over = False

# ستاره‌های پس‌زمینه با حرکت آهسته
stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(0.5, 1.5)) for _ in range(150)]

reset_game()
running = True

while running:
    dt = clock.tick(60) / 60  # برای حرکت نرم‌تر
    screen.fill(BLACK)

    # حرکت ستاره‌ها (پارالاکس خفن)
    for i, (x, y, speed) in enumerate(stars):
        y = (y + speed * 100 * dt) % HEIGHT
        stars[i] = (x, y, speed)
        pygame.draw.circle(screen, WHITE, (int(x), int(y)), 2 if speed > 1 else 1)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if game_over and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reset_game()

    if not game_over:
        keys = pygame.key.get_pressed()
        move_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move_x -= player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move_x += player_speed
        player_x += move_x

        # محدود کردن موشک به صفحه
        player_x = max(player_size, min(WIDTH - player_size, player_x))

        # حرکت سیاه‌چاله (آهسته و ترسناک)
        hole_x += hole_speed_x * 40 * dt
        hole_y += hole_speed_y * 40 * dt
        if hole_x < 100 or hole_x > WIDTH - 100:
            hole_speed_x *= -1
        if hole_y < 100 or hole_y > HEIGHT - 100:
            hole_speed_y *= -1

        # محاسبه جاذبه
        dx = hole_x - player_x
        dy = hole_y - player_y
        distance = math.hypot(dx, dy)

        if distance < 10:
            distance = 10  # جلوگیری از تقسیم بر صفر

        if distance < 60 + player_size:  # برخورد
            game_over = True
        else:
            # قانون عکس مربع با ضریب متعادل
            pull_strength = base_pull_constant / (distance ** 2)
            pull_x = dx * pull_strength * dt
            pull_y = dy * pull_strength * dt
            player_x += pull_x
            player_y += pull_y
            score += 1

    # رسم سیاه‌چاله (با افکت خفن)
    for i in range(6):
        radius = 60 + i * 12
        alpha = max(0, 150 - i * 30)
        s = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*PURPLE, alpha), (radius, radius), radius, max(1, 8 - i))
        screen.blit(s, (hole_x - radius, hole_y - radius))
    
    pygame.draw.circle(screen, BLACK, (int(hole_x), int(hole_y)), 60)
    pygame.draw.circle(screen, RED, (int(hole_x), int(hole_y)), 60, 4)

    # رسم موشک
    pygame.draw.polygon(screen, YELLOW, [
        (player_x, player_y - player_size),
        (player_x - player_size, player_y + player_size),
        (player_x + player_size, player_y + player_size)
    ])

    # شعله موتور (فقط وقتی زنده‌ای)
    if not game_over:
        flame_size = 10 + random.randint(-3, 3)
        pygame.draw.circle(screen, RED, (int(player_x), int(player_y + player_size + 10)), flame_size)
        pygame.draw.circle(screen, ORANGE, (int(player_x), int(player_y + player_size + 13)), flame_size - 3)
        pygame.draw.circle(screen, YELLOW, (int(player_x), int(player_y + player_size + 15)), flame_size - 6)

    # امتیاز
    score_text = font.render(f"امتیاز: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    # صفحه گیم اور
    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        game_over_text = big_font.render("جذب شدی!", True, RED)
        best_text = font.render(f"بهترین: {score}", True, YELLOW)
        restart_text = font.render("دکمه R رو بزن تا دوباره پرواز کنی!", True, WHITE)
        
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 100))
        screen.blit(best_text, (WIDTH//2 - best_text.get_width()//2, HEIGHT//2 - 20))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 40))

    pygame.display.flip()

pygame.quit()