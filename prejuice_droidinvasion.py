# This game is similar to the classic Star Wars game I used to play as a kid. 

# GENERAL COMPONENTS OF THE GAME:
# 1) The player (lightsaber) can move left and right, reflects bullets
# 2) Enemies at the top of the screen, moving down towards the player.
# 3) Enemies shoot red bullets.
# 4) Allow the player to hit back the bullets using the lightsaber to destroy enemies.
# 6) If enemies reach the bottom of the screen, the player loses the game.

#imports
import tkinter as tk
from tkinter import *
import random
from PIL import Image, ImageTk  # Make sure to install the Pillow library for image support
import math

# FILES WHICH WILL NEED TO BE UPDATED ON LOCAL DEVICE:
background_image_direction = "/Users/jacobmillion/Desktop/Github_Sync/Games/Droid_Invasion/nabboo.jpeg"
background_image_direction = "/Users/jacobmillion/Desktop/github/droid_invasion/Droid_Invasion/nabboo.jpeg"
high_score_txt_file = "high_score.txt"
battle_droid_path = "/Users/jacobmillion/Desktop/Github_Sync/Games/Droid_Invasion/droid_image.png"
super_droid_path = "/Users/jacobmillion/Desktop/Github_Sync/Games/Droid_Invasion/super_droid_image.webp"
battle_droid_path = "/Users/jacobmillion/Desktop/github/droid_invasion/Droid_Invasion/droid_image.png"
super_droid_path = "/Users/jacobmillion/Desktop/github/droid_invasion/Droid_Invasion/super_droid_image.webp"
########################################################

# Boolean to track when the game is over
game_over = False

# Creating root window and canvas
root = tk.Tk()
root.title("Droid Invasion")
HEIGHT = 700
WIDTH = 600
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT)
canvas.pack()

# Background image
bg_image = Image.open(background_image_direction)
bg_image = bg_image.resize((WIDTH, 700), Image.BICUBIC)
bg_image.putalpha(30)  # alpha value (0 for fully transparent, 255 for fully opaque)
bg_image = ImageTk.PhotoImage(bg_image)
background = canvas.create_image(0, 0, anchor=NW, image=bg_image)

# Global variables for points and high score,
# tracks the number of enemies killed
points = 0
high_score = 0

# Loads high score from txt file
def load_high_score():
    global high_score
    try:
        with open(high_score_txt_file, "r") as file:
            high_score = int(file.read())
    except FileNotFoundError:
        high_score = 0

# Save the high score to the file and update it if necessary
def save_and_update_high_score():
    global high_score
    if points > high_score:
        high_score = points
        update_high_score_label()
        canvas.create_text(WIDTH // 2, HEIGHT // 2 + 50, text="NEW HIGH SCORE!", font=("Arial", 20), fill="green")
        with open(high_score_txt_file, "w") as file:
            file.write(str(high_score))
            file.flush() 

# Resets the high score 
def reset_high_score():
    global high_score 
    high_score = 0
    with open(high_score_txt_file, "w") as file:
        file.write(str(high_score))
        file.flush()
    update_high_score_label()

# Points and high score label, to display on the screen
points_frame = tk.Frame(root, bg="black")
points_frame.pack(side=tk.TOP, fill=tk.X)

points_label = tk.Label(points_frame, text="Points: " + str(points), font=("Arial", 14), bg="black", fg="white")
points_label.grid(row=0, column=0, padx=(WIDTH // 2), pady=5)  

high_score_label = tk.Label(points_frame, text="High Score: " + str(high_score), font=("Arial", 14), bg="black", fg="white")
high_score_label.grid(row=0, column=1, padx=(WIDTH // 2), pady=5)  

# Updates the labels with the current points / high score value
def update_points_label():
    points_label.config(text="Points: " + str(points))

def update_high_score_label():
    high_score_label.config(text="High Score: " + str(high_score))

# Types of droids and their probability
droid_types = [
    {"type": "battle_droid", "probability": 0.95},
    {"type": "super_droid", "probability": 0.05}
]

# Player settings 
player_height = 10
player_width = 100
player_speed = 20  # Updated speed
circle_radius = player_height // 2
SABERCOLOR = "springgreen"

floor_displacement = 5

center_x = WIDTH // 2
right_x = center_x + (player_width / 2)
right_y = HEIGHT - floor_displacement
left_x = center_x - (player_width / 2)
left_y = HEIGHT - player_height - floor_displacement

# Draw the circles for the lightsaber shape
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

# Draws the player using the above to ensure it is placed in the center
player = canvas.create_rectangle(
    left_x, circle_y - circle_radius,
    right_x, circle_y + circle_radius,
    fill=SABERCOLOR
)

player_center_x = (canvas.coords(player)[0] + canvas.coords(player)[2]) / 2

player_center_drawing = canvas.create_rectangle( 
    player_center_x - 2, HEIGHT - player_height - 5, 
    player_center_x + 2, HEIGHT - player_height + (player_height / 2), 
    fill="black"
)

# Player movement
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
canvas.focus_set()

# Bullet class
class Bullet:
    def __init__(self, canvas, x, y):
        self.bullet_speed = 9  # Updated speed
        self.x_coord = x 
        self.y_coord = y 
        self.fill = "red"

        self.x_speed = 0
        self.y_speed = 0

        self.reflected = False  # If True, can damage droids

        self.bullet = canvas.create_oval(
            self.x_coord, self.y_coord, 
            self.x_coord + 3, self.y_coord + 20, 
            fill=self.fill
        )

    def move(self):
        # If not reflected, move down; otherwise, move in reflected direction
        if not self.reflected:
            self.y_coord += self.bullet_speed
            canvas.move(self.bullet, 0, self.bullet_speed)
        else:
            self.x_coord += self.x_speed
            self.y_coord += self.y_speed
            canvas.move(self.bullet, self.x_speed, self.y_speed)

    def reflect(self):
        self.reflected = True
        player_center_x = (canvas.coords(player)[0] + canvas.coords(player)[2]) / 2
        relative_hit_position = self.x_coord - player_center_x 
        reflection_angle = math.atan2(relative_hit_position, player_width / 2)

        self.x_speed = math.sin(reflection_angle) * self.bullet_speed
        self.y_speed = -math.cos(reflection_angle) * self.bullet_speed

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

# Create bullets from enemy
def enemy_shoot(enemy):
    x = canvas.coords(enemy.droid)[0] + enemy.droid_width / 2  # midpoint of droid
    y = canvas.coords(enemy.droid)[1]  # top left
    bullet = Bullet(canvas, x, y)
    enemy_bullets.append(bullet)

# Move enemy bullets loop
def move_enemy_bullets():
    for bullet in enemy_bullets[:]:
        if bullet.get_y() >= HEIGHT or bullet.get_x() <= 0 or bullet.get_x() >= WIDTH:
            enemy_bullets.remove(bullet)
            canvas.delete(bullet.bullet)
        else:
            bullet.move()

    # Check for collisions with player and enemies
    check_collision_with_player()
    check_collision_with_enemies()

    # Repeat the function, keep bullets moving
    bullet_movement_delay = 50
    canvas.after(bullet_movement_delay, move_enemy_bullets)

# Checks for collision with enemies
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

            if (
                bullet_x >= enemy_x - enemy.droid_width and bullet_x <= enemy_x + enemy.droid_width and
                bullet_y <= enemy_y + (enemy.droid_height // 2) and bullet_y >= enemy_y - (enemy.droid_height // 2)
            ):
                # Bullet hit enemy
                damage = 1
                enemy.deal_damage(damage)
                enemy_bullets.remove(bullet)
                canvas.delete(bullet.bullet)
                if enemy.health == 0:
                    points += 1
                    update_points_label()
                    enemies.remove(enemy)
                    canvas.delete(enemy.droid)

# Checks for collision with player
def check_collision_with_player():
    for bullet in enemy_bullets:
        if bullet.reflected:
            continue
        bullet_x = bullet.get_x()
        bullet_y = bullet.get_y()
        player_x = canvas.coords(player)[0]
        player_y = canvas.coords(player)[1]

        if (
            bullet_x >= player_x and bullet_x <= player_x + player_width and
            bullet_y >= (player_y - 20) and bullet_y <= (player_y + player_height + 20)
        ):
            # Bullet hit the saber / player, reflect the bullet
            bullet.reflect()

# Droid class
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

        # Create the droid on the canvas
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

# Create enemies list
enemies = []

def create_enemy(droid_type):
    global game_over

    if game_over:
        return

    if droid_type == "battle_droid":
        droid_width = 35
        droid_height = 60
        speed = 5.8  # Updated speed
        health = 1
        path = battle_droid_path
        droid = Droid(droid_width, droid_height, canvas, random.randint(droid_width, WIDTH - droid_width), 0, speed, health, path)
        enemies.append(droid)

    elif droid_type == "super_droid":
        droid_width = 50
        droid_height = 70
        speed = 2  # Updated speed
        health = 2
        path = super_droid_path
        droid = Droid(droid_width, droid_height, canvas, random.randint(droid_width, WIDTH - droid_width), 0, speed, health, path)
        enemies.append(droid)        
    # Add more conditions for other droid types if needed

    # Schedule the next enemy creation
    next_droid_type = random.choices(
        [d["type"] for d in droid_types],
        weights=[d["probability"] for d in droid_types]
    )[0]
    delay = random.randint(4400, 6000)
    canvas.after(delay, lambda: create_enemy(next_droid_type))

# Moves enemies loop
def move_enemies():
    global game_over

    for enemy in enemies[:]:
        enemy.change_y()

        # Check if an enemy reaches the bottom of the screen
        if canvas.coords(enemy.droid)[1] >= HEIGHT - 20:
            game_over = True

        # Randomly shoot bullets with a certain probability
        if random.random() < 0.05:  # Single probability check for shooting
            enemy_shoot(enemy)

    # Check for game over
    if game_over:
        canvas.create_text(WIDTH // 2, HEIGHT // 2, text="GAME OVER", font=("Arial", 30), fill="red")
        save_and_update_high_score()
        return  # Stop the game loop

    # Repeat the function after 200 milliseconds (adjust as needed)
    canvas.after(200, move_enemies)

##########################################################

# Running the game
load_high_score()
update_high_score_label()
create_enemy("battle_droid")
move_enemies()
move_enemy_bullets()
root.mainloop()

