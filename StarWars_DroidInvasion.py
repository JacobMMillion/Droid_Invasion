# This game is similar to the classic star wars game I used to play as a kid. 

# GENERAL COMPONENTS OF THE GAME:
# 1) The player (lightsaber)  can move left and right, reflects bullets
# 2) Enemies at the top of the screen, moving down towards the player.
# 3) Enemies shoot red bullets.
# 4) Allow the player to hit back the bullets using the lightsaber to destroy enemies.
# 6) If enemies reach the bottom of the screen, the player loses the game.

#imports
import tkinter as tk
from tkinter import *
import random
from PIL import Image, ImageTk  # Make sure to install Pillow for image support
import math
import time  # For tracking elapsed time
from playsound import playsound

# FILES – UPDATE THESE PATHS ON YOUR LOCAL DEVICE:
background_image_direction = "/Users/jacobmillion/Desktop/github/droid_invasion/Droid_Invasion/nabboo.jpeg"
high_score_txt_file = "high_score.txt"
battle_droid_path = "/Users/jacobmillion/Desktop/github/droid_invasion/Droid_Invasion/droid_image.png"
super_droid_path = "/Users/jacobmillion/Desktop/github/droid_invasion/Droid_Invasion/super_droid_image.webp"
shoot_audio_file_path = "/Users/jacobmillion/Desktop/github/droid_invasion/Droid_Invasion/blaster.mp3"
explosion_audio_path = "/Users/jacobmillion/Desktop/github/droid_invasion/Droid_Invasion/explosion.wav"
reflect_audio_path = "/Users/jacobmillion/Desktop/github/droid_invasion/Droid_Invasion/reflect.wav"
########################################################

# Global game state variables
game_over = False
start_time = time.time()
points = 0
high_score = 0
enemies = []
enemy_bullets = []
particles = []
restart_button_global = None
game_over_text_id = None  # Will hold the ID of the "GAME OVER" text

# Creating root window and canvas
root = tk.Tk()
root.title("Droid Invasion")
HEIGHT = 700
WIDTH = 600
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT)
canvas.pack()

# Load and display the background image
bg_image = Image.open(background_image_direction)
bg_image = bg_image.resize((WIDTH, 700), Image.BICUBIC)
bg_image.putalpha(30)  # Set transparency
bg_image = ImageTk.PhotoImage(bg_image)
background = canvas.create_image(0, 0, anchor=NW, image=bg_image)

# Score and high score management
def load_high_score():
    global high_score
    try:
        with open(high_score_txt_file, "r") as file:
            high_score = int(file.read())
    except FileNotFoundError:
        high_score = 0

def save_and_update_high_score():
    global high_score
    if points > high_score:
        high_score = points
        update_high_score_label()
        canvas.create_text(WIDTH // 2, HEIGHT // 2 + 50, text="NEW HIGH SCORE!", font=("Arial", 20), fill="green")
        with open(high_score_txt_file, "w") as file:
            file.write(str(high_score))
            file.flush()

def reset_high_score():
    global high_score 
    high_score = 0
    with open(high_score_txt_file, "w") as file:
        file.write(str(high_score))
        file.flush()
    update_high_score_label()

# Frame for score display (adjusts with window size)
points_frame = tk.Frame(root, bg="black")
points_frame.pack(side=tk.TOP, fill='x', padx=10, pady=5)  # Expands with window width

# Labels for score and high score, now aligned properly
points_label = tk.Label(points_frame, text="Points: " + str(points), font=("Arial", 14), bg="black", fg="white")
points_label.pack(side=LEFT, padx=20, anchor="w")  # Aligns to the left

high_score_label = tk.Label(points_frame, text="High Score: " + str(high_score), font=("Arial", 14), bg="black", fg="white")
high_score_label.pack(side=RIGHT, padx=20, anchor="e")  # Aligns to the right

def update_points_label():
    points_label.config(text="Points: " + str(points))

def update_high_score_label():
    high_score_label.config(text="High Score: " + str(high_score))

# Player settings and drawing
player_height = 10
player_width = 100
player_speed = 20
circle_radius = player_height // 2
SABERCOLOR = "springgreen"
floor_displacement = 5

center_x = WIDTH // 2
right_x = center_x + (player_width / 2)
left_x = center_x - (player_width / 2)
circle_y = HEIGHT - player_height // 2 - floor_displacement

left_circle = canvas.create_oval(
    left_x - circle_radius, circle_y - circle_radius,
    left_x + circle_radius, circle_y + circle_radius,
    fill=SABERCOLOR
)
right_circle = canvas.create_oval(
    right_x - circle_radius, circle_y - circle_radius,
    right_x + circle_radius, circle_y + circle_radius,
    fill=SABERCOLOR
)
player = canvas.create_rectangle(
    left_x, circle_y - circle_radius,
    right_x, circle_y + circle_radius,
    fill=SABERCOLOR
)
player_center_x = (left_x + right_x) / 2
player_center_drawing = canvas.create_rectangle( 
    player_center_x - 2, HEIGHT - player_height - 5, 
    player_center_x + 2, HEIGHT - player_height + (player_height / 2), 
    fill="black"
)

# Player movement functions; binding both A/D and arrow keys
def move_left(event):
    canvas.move(player, -player_speed, 0)
    canvas.move(left_circle, -player_speed, 0)
    canvas.move(right_circle, -player_speed, 0)
    canvas.move(player_center_drawing, -player_speed, 0)

def move_right(event):
    canvas.move(player, player_speed, 0)
    canvas.move(left_circle, player_speed, 0)
    canvas.move(right_circle, player_speed, 0)
    canvas.move(player_center_drawing, player_speed, 0)

canvas.bind("<a>", move_left)
canvas.bind("<d>", move_right)
canvas.bind("<Left>", move_left)
canvas.bind("<Right>", move_right)
canvas.focus_set()

# ---------------------------
# Particle Explosion / Sparks Effect
# ---------------------------
class Particle:
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.size = random.randint(2, 5)
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = random.uniform(2, 5)
        self.lifetime = random.randint(10, 20)  # Lifetime in update frames
        self.color = random.choice(["orange", "yellow", "red"])
        self.id = canvas.create_oval(
            self.x, self.y, self.x + self.size, self.y + self.size,
            fill=self.color, outline=""
        )
    def update(self):
        dx = self.speed * math.cos(self.angle)
        dy = self.speed * math.sin(self.angle)
        self.x += dx
        self.y += dy
        self.canvas.move(self.id, dx, dy)
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.canvas.delete(self.id)
            return True  # Particle expired
        return False

def update_particles():
    global particles
    for particle in particles[:]:
        if particle.update():
            particles.remove(particle)
    canvas.after(50, update_particles)

def create_particle_explosion(x, y, count=15):
    for i in range(count):
        p = Particle(canvas, x, y)
        particles.append(p)

update_particles()

# ---------------------------
# Bullet class
# ---------------------------
class Bullet:
    def __init__(self, canvas, x, y):
        self.bullet_speed = 9
        self.x_coord = x 
        self.y_coord = y 
        self.fill = "red"
        self.x_speed = 0
        self.y_speed = 0
        self.reflected = False  # When reflected, bullet can damage droids
        self.bullet = canvas.create_oval(
            self.x_coord, self.y_coord, 
            self.x_coord + 3, self.y_coord + 20, 
            fill=self.fill
        )
    def move(self):
        if not self.reflected:
            self.y_coord += self.bullet_speed
            canvas.move(self.bullet, 0, self.bullet_speed)
        else:
            self.x_coord += self.x_speed
            self.y_coord += self.y_speed
            canvas.move(self.bullet, self.x_speed, self.y_speed)
    def reflect(self):
        self.reflected = True
        playsound(reflect_audio_path, block=False)
        player_coords = canvas.coords(player)
        player_left_x = player_coords[0]
        player_right_x = player_coords[2]
        player_center_x = (player_left_x + player_right_x) / 2

        # Determine how far from center the bullet hit
        relative_hit = self.x_coord - player_center_x
        saber_half_width = player_width / 2

        # Normalize and apply a gentler curve to maintain reflection consistency
        normalized_relative_hit = relative_hit / saber_half_width
        normalized_relative_hit = max(-1, min(1, normalized_relative_hit))

        # Adjust curvature to keep extreme reflections but avoid glitches
        extreme_reflection_factor = 1.3  # Keep it strong, but not over-exaggerated
        adjusted_hit = (normalized_relative_hit * extreme_reflection_factor) ** 2  # Changed from **3 to **2

        # Maintain sign to preserve direction
        if normalized_relative_hit < 0:
            adjusted_hit = -adjusted_hit

        # Allow sharper deflections at the saber tips
        max_reflection_angle = math.radians(85)  # Slightly more than before
        reflection_angle = adjusted_hit * max_reflection_angle

        # Ensure bullets always reflect UP
        self.x_speed = self.bullet_speed * math.sin(reflection_angle)
        self.y_speed = -abs(self.bullet_speed * math.cos(reflection_angle))  # Ensure it's always negative

        # Move immediately to prevent "sticking"
        self.x_coord += self.x_speed
        self.y_coord += self.y_speed
        canvas.move(self.bullet, self.x_speed, self.y_speed)
    def get_x(self):
        return self.x_coord
    def get_y(self):
        return self.y_coord
    def get_coordinates(self):
        return canvas.coords(self.bullet)

enemy_bullets = []
def enemy_shoot(enemy):
    x = canvas.coords(enemy.droid)[0] + enemy.droid_width / 2  # Midpoint of droid
    y = canvas.coords(enemy.droid)[1]  # Top left of droid image
    bullet = Bullet(canvas, x, y)
    enemy_bullets.append(bullet)

    playsound(shoot_audio_file_path, block=False)

def move_enemy_bullets():
    try:
        # Iterate over a copy so removals don't affect the loop
        for bullet in enemy_bullets[:]:
            if bullet.get_y() >= HEIGHT or bullet.get_x() <= 0 or bullet.get_x() >= WIDTH:
                enemy_bullets.remove(bullet)
                canvas.delete(bullet.bullet)
            else:
                bullet.move()
        check_collision_with_player()
        check_collision_with_enemies()
    except Exception as e:
        print("Error in move_enemy_bullets:", e)
    finally:
        canvas.after(50, move_enemy_bullets)

def check_collision_with_enemies():
    global points
    for bullet in enemy_bullets[:]:
        if not bullet.reflected:
            continue
        bullet_x = bullet.get_x()
        bullet_y = bullet.get_y()
        for enemy in enemies[:]:
            enemy_x = enemy.get_x()
            enemy_y = enemy.get_y()
            if (bullet_x >= enemy_x - enemy.droid_width and bullet_x <= enemy_x + enemy.droid_width and
                bullet_y <= enemy_y + (enemy.droid_height // 2) and bullet_y >= enemy_y - (enemy.droid_height // 2)):
                damage = 1
                enemy.deal_damage(damage)
                enemy_bullets.remove(bullet)
                canvas.delete(bullet.bullet)
                if enemy.health <= 0:
                    points += 1
                    update_points_label()
                    # Full explosion on kill uses 15 particles
                    create_particle_explosion(enemy.get_x(), enemy.get_y(), count=15)
                    playsound(explosion_audio_path, block=False)
                    enemies.remove(enemy)
                    canvas.delete(enemy.droid)
                else:
                    # For non-lethal hits, emit reduced sparks (3 particles)
                    create_particle_explosion(enemy.get_x(), enemy.get_y(), count=3)

def check_collision_with_player():
    for bullet in enemy_bullets:
        if bullet.reflected:
            continue
        bullet_x = bullet.get_x()
        bullet_y = bullet.get_y()
        player_coords = canvas.coords(player)
        player_x = player_coords[0]
        player_y = player_coords[1]
        if (bullet_x >= player_x and bullet_x <= player_x + player_width and
            bullet_y >= (player_y - 20) and bullet_y <= (player_y + player_height + 20)):
            bullet.reflect()

# ---------------------------
# Droid class
# ---------------------------
class Droid:
    def __init__(self, width, height, canvas, x, y, speed, health, image_path):
        self.droid_width = width
        self.droid_height = height
        self.droid_speed = speed
        self.x_coord = x
        self.y_coord = y
        self.health = health
        self.droid_image = Image.open(image_path)
        self.droid_image = self.droid_image.resize((self.droid_width, self.droid_height), Image.BICUBIC)
        self.droid_image = ImageTk.PhotoImage(self.droid_image)
        self.droid = canvas.create_image(self.x_coord, self.y_coord, image=self.droid_image)
    def change_x(self, num):
        self.x_coord += num
        canvas.move(self.droid, num, 0)
    def change_y(self):
        self.y_coord += self.droid_speed
        canvas.move(self.droid, 0, self.droid_speed)
    def get_x(self):
        return self.x_coord
    def get_y(self):
        return self.y_coord
    def get_speed(self):
        return self.droid_speed
    def get_image(self):
        return self.droid_image
    def get_coordinates(self):
        return canvas.coords(self.droid)
    def deal_damage(self, damage):
        self.health -= damage

def create_enemy(droid_type):
    global game_over
    if game_over:
        return
    if droid_type == "battle_droid":
        droid_width = 35
        droid_height = 60
        speed = 4.5
        health = 1
        path = battle_droid_path
        droid = Droid(droid_width, droid_height, canvas,
                      random.randint(droid_width, WIDTH - droid_width), 0,
                      speed, health, path)
        enemies.append(droid)
    elif droid_type == "super_droid":
        droid_width = 50
        droid_height = 70
        speed = 1.9    # slowed down by 0.1 (from 2 to 1.9)
        health = 3     # increased health from 2 to 3
        path = super_droid_path
        droid = Droid(droid_width, droid_height, canvas,
                      random.randint(droid_width, WIDTH - droid_width), 0,
                      speed, health, path)
        enemies.append(droid)
    # Dynamic probability adjustment over 4 minutes (240 seconds):
    # Initially, 20% super droids (80% battle), scaling linearly to 80% super droids.
    elapsed = time.time() - start_time
    factor_prob = min(elapsed / 240.0, 1.0)
    new_super_prob = 0.20 + (0.80 - 0.20) * factor_prob
    new_battle_prob = 1.0 - new_super_prob
    # Dynamic spawn delay – initial delay between 3000 and 7000 ms becomes faster over time.
    factor_delay = 2 ** (elapsed / 240.0)
    lower_bound = 3000 / factor_delay
    upper_bound = 7000 / factor_delay
    delay = random.randint(int(lower_bound), int(upper_bound))
    droid_choice = random.choices(
        ["battle_droid", "super_droid"],
        weights=[new_battle_prob, new_super_prob]
    )[0]
    canvas.after(delay, lambda: create_enemy(droid_choice))

def move_enemies():
    global game_over, game_over_text_id
    for enemy in enemies:
        enemy.change_y()
        if canvas.coords(enemy.droid)[1] >= HEIGHT - 20:
            game_over = True
        # Reduced firing frequency
        if random.random() < 0.04:
            enemy_shoot(enemy)
    if game_over:
        # Create game over text and store its ID so it can be removed later.
        game_over_text_id = canvas.create_text(WIDTH // 2, HEIGHT // 2, text="GAME OVER", font=("Arial", 30), fill="red")
        save_and_update_high_score()
        show_restart_button()
        return
    canvas.after(200, move_enemies)

# ---------------------------
# Restart Button & Game Restart
# ---------------------------
def show_restart_button():
    global restart_button_global
    # Place the button slightly lower than center
    restart_button = tk.Button(root, text="Restart", font=("Arial", 14), command=restart_game)
    restart_button.place(relx=0.5, rely=0.57, anchor="center")
    restart_button_global = restart_button

def restart_game():
    global game_over, points, enemies, enemy_bullets, start_time, game_over_text_id
    game_over = False
    points = 0
    update_points_label()
    # Remove all enemy droids.
    for enemy in enemies:
        canvas.delete(enemy.droid)
    enemies.clear()
    # Remove all enemy bullets.
    for bullet in enemy_bullets:
        canvas.delete(bullet.bullet)
    enemy_bullets.clear()
    # Remove game over text if it exists.
    if game_over_text_id is not None:
        canvas.delete(game_over_text_id)
    # Destroy the restart button.
    if restart_button_global is not None:
        restart_button_global.destroy()
    # Reset the start time.
    start_time = time.time()
    # Reset the player's position and associated items.
    canvas.coords(player, left_x, circle_y - circle_radius, right_x, circle_y + circle_radius)
    canvas.coords(left_circle, left_x - circle_radius, circle_y - circle_radius, left_x + circle_radius, circle_y + circle_radius)
    canvas.coords(right_circle, right_x - circle_radius, circle_y - circle_radius, right_x + circle_radius, circle_y + circle_radius)
    new_player_center_x = (left_x + right_x) / 2
    canvas.coords(player_center_drawing, new_player_center_x - 2, HEIGHT - player_height - 5, new_player_center_x + 2, HEIGHT - player_height + (player_height / 2))
    # Start enemy generation and movement again.
    create_enemy("battle_droid")
    move_enemies()

# ---------------------------
# Start the Game
# ---------------------------
load_high_score()
update_high_score_label()
create_enemy("battle_droid")
move_enemies()
move_enemy_bullets()
root.mainloop()
