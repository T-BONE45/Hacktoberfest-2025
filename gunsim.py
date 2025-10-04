# projectile_sim.py
# Educational projectile simulator (non-weaponized)
# Requires: Python 3.x and pygame (pip install pygame)

import pygame
import math
import sys

# --- Configuration ---
WIDTH, HEIGHT = 1000, 600
GROUND_Y = HEIGHT - 50
FPS = 60
SCALE = 1.0  # pixels per meter (adjust to zoom)

# Colors
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GREEN = (50, 200, 70)
RED = (220, 60, 60)
BLUE = (60, 140, 220)
GRAY = (200, 200, 200)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Projectile Physics Simulator — Educational")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 20)

# --- Simulation state ---
angle_deg = 45.0
speed = 40.0  # m/s
wind = 0.0    # m/s (positive to the right)
drag_coef = 0.05  # simple linear drag coefficient
projectiles = []  # active projectiles (each is a dict)

GRAVITY = 9.81  # m/s^2

launcher_pos = (50, GROUND_Y)  # pixels


def draw_text(s, x, y, color=BLACK):
    img = font.render(s, True, color)
    screen.blit(img, (x, y))


def reset_sim():
    global projectiles
    projectiles = []


def spawn_projectile(angle_deg, speed):
    # convert to m/s and meters (we'll treat 1 pixel ~ 1 meter * SCALE)
    angle_rad = math.radians(angle_deg)
    vx = speed * math.cos(angle_rad) + wind
    vy = -speed * math.sin(angle_rad)  # negative because screen y grows downward
    p = {
        "x": launcher_pos[0] / SCALE,
        "y": (launcher_pos[1]) / SCALE,
        "vx": vx,
        "vy": vy,
        "time": 0.0
    }
    projectiles.append(p)


def update_projectiles(dt):
    to_remove = []
    for p in projectiles:
        # simple physics with linear drag: F_drag = -k * v
        vx = p["vx"]
        vy = p["vy"]

        # acceleration
        ax = -drag_coef * vx
        ay = GRAVITY - drag_coef * vy

        # integrate (semi-implicit Euler)
        p["vx"] += ax * dt
        p["vy"] += ay * dt

        p["x"] += p["vx"] * dt * SCALE
        p["y"] += p["vy"] * dt * SCALE
        p["time"] += dt

        # if hits ground
        if p["y"] >= GROUND_Y:
            p["y"] = GROUND_Y
            p["vx"] *= 0.25  # bounce loss
            p["vy"] *= -0.2
            # remove small residual motion
            if abs(p["vx"]) < 0.5 and abs(p["vy"]) < 0.5:
                to_remove.append(p)

        # if off-screen to the right or left for long time, remove
        if p["x"] < -100 or p["x"] > WIDTH + 100 or p["time"] > 30:
            to_remove.append(p)

    for p in to_remove:
        if p in projectiles:
            projectiles.remove(p)


def draw_ground():
    pygame.draw.rect(screen, GREEN, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))


def draw_launcher(angle_deg):
    x, y = launcher_pos
    length = 40
    end_x = x + length * math.cos(math.radians(-angle_deg))
    end_y = y + length * math.sin(math.radians(-angle_deg))
    pygame.draw.line(screen, BLACK, (x, y), (end_x, end_y), 6)
    pygame.draw.circle(screen, GRAY, (int(x), int(y)), 8)


def draw_projectiles():
    for p in projectiles:
        px = int(p["x"])
        py = int(p["y"])
        pygame.draw.circle(screen, RED, (px, py), 6)
        # draw trail (simple)
        if p["time"] > 0:
            for t in range(1, 6):
                tx = int(p["x"] - p["vx"] * t * 0.02 * SCALE)
                ty = int(p["y"] - p["vy"] * t * 0.02 * SCALE)
                pygame.draw.circle(screen, (200, 120, 120), (tx, ty), max(1, 4 - t))


def draw_ui():
    draw_text(f"Angle: {angle_deg:.1f}° (Left/Right keys)", 10, 10)
    draw_text(f"Speed: {speed:.1f} m/s (Up/Down keys)", 10, 30)
    draw_text(f"Wind: {wind:.1f} m/s (A/D keys)", 10, 50)
    draw_text(f"Drag coef: {drag_coef:.3f} (W/S keys)", 10, 70)
    draw_text("Space: launch projectile    R: reset    Esc: quit", 10, 100)

    # show small legend
    draw_text(f"Projectiles: {len(projectiles)}", WIDTH - 160, 10)
    # predicted range (approximate, ignoring drag)
    angle_r = math.radians(angle_deg)
    if drag_coef < 0.0001:
        # if no drag, compute analytic range
        v = speed
        range_m = (v ** 2) * math.sin(2 * angle_r) / GRAVITY
        draw_text(f"Ideal range (no drag): {range_m:.1f} m", WIDTH - 260, 30)
    else:
        draw_text(f"(Drag active: simulation estimate only)", WIDTH - 300, 30)


def main_loop():
    global angle_deg, speed, wind, drag_coef
    running = True
    paused = False
    while running:
        dt = clock.tick(FPS) / 1000.0  # seconds
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    spawn_projectile(angle_deg, speed)
                elif event.key == pygame.K_r:
                    reset_sim()
                elif event.key == pygame.K_p:
                    paused = not paused

        # continuous key presses
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            angle_deg = max(1.0, angle_deg - 30.0 * dt)
        if keys[pygame.K_RIGHT]:
            angle_deg = min(89.0, angle_deg + 30.0 * dt)
        if keys[pygame.K_UP]:
            speed = min(300.0, speed + 30.0 * dt)
        if keys[pygame.K_DOWN]:
            speed = max(1.0, speed - 30.0 * dt)
        if keys[pygame.K_a]:
            wind -= 10.0 * dt
        if keys[pygame.K_d]:
            wind += 10.0 * dt
        if keys[pygame.K_w]:
            drag_coef = max(0.0, drag_coef - 0.02 * dt)
        if keys[pygame.K_s]:
            drag_coef = min(1.0, drag_coef + 0.02 * dt)

        if not paused:
            update_projectiles(dt)

        # draw
        screen.fill(WHITE)
        draw_ground()
        draw_launcher(angle_deg)
        draw_projectiles()
        draw_ui()

        # draw wind indicator
        wind_text = f"Wind: {wind:.1f} m/s"
        draw_text(wind_text, WIDTH - 160, HEIGHT - 30)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main_loop()
