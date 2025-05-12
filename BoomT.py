from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_9_BY_15
import random
import math


rooms=[(-1500, 400, 900, 900),(-1500, -1100, 900, 900),(800, -1100, 900, 900)]
key_states = {b'w': False, b'a': False, b's': False, b'd': False}

room4_x, room4_y, room4_width, room4_depth = -1800, 2500, 1500, 1500
orange_screen_flag = False
explosive_drums = [(-1100, 50), (-1400, -400), (100, 100)]
crates = [
    (-700, -800, 70),
    (-700, -1000, 70),
    (-700, -600, 70),
    (-700, -400, 70),
    (800, -1100, 70),
    (-1360.821003117057, 968.3919648628456, 70),
    (-1360, 768.3919648628456, 70),
    (-1360.821003117057, 568.3919648628456, 70),
    (-663.312606397818, 1200.4214978749658, 70),
    (-863.312606397818, 1200.4214978749658, 70)
]

health_packs = [(-663.312606397818, 1200.4214978749658, 70, 25),
                (-1360.821003117057, 568.3919648628456, 70, 25),
                (-863.312606397818, 1200.4214978749658, 70, 25)]

keys = [(-1360, 768.3919648628456, 70)]

enemy_respawn_timer = 0
ENEMY_RESPAWN_DELAY = 60  # Frames between spawning enemies (about 2 seconds at 60fps)
MAX_ENEMIES = 6

left_mouse_pressed = False
fire_cooldown = 0
FIRE_RATE = 1

scaling_factor = 1
gun_rotation = 0
game_over = True
enemy2_pos = [0, 0]
terrain_map = {}
tree_positions = []
cam_radius = 600
cam_angle = 0
cam_height = 600
cam_elev = 50
MIN_ELEV_DEG = 15
MAX_ELEV_DEG = 80
fovY = 105


BACK_OFFSET = 40
LOOK_DISTANCE = 100
HEAD_HEIGHT = 145


GRID_LENGTH = 500
WALL_THICK = 5
MARGIN_X = 30
MARGIN_FRONT = 57
MARGIN_BACK = 12
enemies = []
player_pos = [0, 0]
player_angle = 0

enemy_scale_factor = 1
enemy_scale_direction = 1
enemy_speed = 10
Object_collision=False
player_health = 5000
player_key = 0
score = 0
player_dead = False
missed_bullets = 0
BULLET_SPEED = 70
BULLET_SIZE = 7
BULLET_LIFE = 25
bullets = []
def is_colliding_with_objects(x,y):
     for i in crates:
         if abs(x - i[0]+10 )<50 and abs(y - i[1]+10)<50:
             print("collison")
             return True
     for room in rooms:
        room_x, room_y, room_w, room_d = room
        door_width = 100
        door_start_x = room_x + room_w - door_width
        door_end_x = room_x + room_w
        wall_thickness = 20

        # === Left Wall ===
        if (room_y <= y <= room_y + room_d and
            room_x - wall_thickness <= x <= room_x + wall_thickness):
            print("collision with left wall")
            return True

        # === Right Wall ===
        if (room_y <= y <= room_y + room_d and
            room_x + room_w - wall_thickness <= x <= room_x + room_w + wall_thickness):
            print("collision with right wall")
            return True

        # === Back Wall ===
        if (room_x <= x <= room_x + room_w and
            room_y + room_d - wall_thickness <= y <= room_y + room_d + wall_thickness):
            print("collision with back wall")
            return True

        # === Front Wall (with door gap exception) ===
        if (room_x <= x <= room_x + room_w and
            room_y - wall_thickness <= y <= room_y + wall_thickness):
            if not (door_start_x <= x <= door_end_x):
                print("collision with front wall")
                return True
            else:
                print("passing through door")

     return False  # no collision
 
def spawn_single_enemy():
    enemy_types = [
        {'type': 'red', 'scale': 2.0, 'health': 10},
        {'type': 'purple', 'scale': 0.7, 'health': 2},
        {'type': 'yellow', 'scale': 1.0, 'health': 5},
    ]
    enemy_type = random.choice(enemy_types)

    x = random.randint(-GRID_LENGTH - 500, GRID_LENGTH + 500)
    y = random.randint(-GRID_LENGTH - 500, GRID_LENGTH + 500)
    initial_angle = random.randint(0, 359)  # Random initial orientation

    tile_size = 50
    tile_x = (x // tile_size) * tile_size
    tile_y = (y // tile_size) * tile_size

    if (tile_x, tile_y) in terrain_map and terrain_map[(tile_x, tile_y)] == 'water':
        x = random.randint(-GRID_LENGTH, GRID_LENGTH)
        y = random.randint(-GRID_LENGTH, GRID_LENGTH)

    # Add the new enemy with health information
    enemies.append((x, y, enemy_type['type'], enemy_type['scale'], initial_angle, enemy_type['health']))


def check_enemy_respawn():
    """Check if new enemies should be spawned"""
    global enemy_respawn_timer

    # If below maximum enemies, decrement timer
    if len(enemies) < MAX_ENEMIES:
        enemy_respawn_timer -= 1

        # When timer reaches zero, spawn a new enemy and reset timer
        if enemy_respawn_timer <= 0:
            spawn_single_enemy()
            enemy_respawn_timer = ENEMY_RESPAWN_DELAY


def draw_chest(x, y, z=0, length=70, width=50, height=40, top_height=20):

    glColor3f(0.545, 0.271, 0.075)

    glPushMatrix()
    glTranslatef(x, y, z)

    glBegin(GL_QUADS)

    # Front face
    glVertex3f(-length / 2, -width / 2, 0)
    glVertex3f(length / 2, -width / 2, 0)
    glVertex3f(length / 2, width / 2, 0)
    glVertex3f(-length / 2, width / 2, 0)

    # Back face
    glVertex3f(-length / 2, -width / 2, -height)
    glVertex3f(length / 2, -width / 2, -height)
    glVertex3f(length / 2, width / 2, -height)
    glVertex3f(-length / 2, width / 2, -height)

    # Left face
    glVertex3f(-length / 2, -width / 2, 0)
    glVertex3f(-length / 2, -width / 2, -height)
    glVertex3f(-length / 2, width / 2, -height)
    glVertex3f(-length / 2, width / 2, 0)

    # Right face
    glVertex3f(length / 2, -width / 2, 0)
    glVertex3f(length / 2, -width / 2, -height)
    glVertex3f(length / 2, width / 2, -height)
    glVertex3f(length / 2, width / 2, 0)

    # Top face
    glVertex3f(-length / 2, width / 2, 0)
    glVertex3f(length / 2, width / 2, 0)
    glVertex3f(length / 2, width / 2, -height)
    glVertex3f(-length / 2, width / 2, -height)

    # Bottom face
    glVertex3f(-length / 2, -width / 2, 0)
    glVertex3f(length / 2, -width / 2, 0)
    glVertex3f(length / 2, -width / 2, -height)
    glVertex3f(-length / 2, -width / 2, -height)

    glEnd()

    glColor3f(0.8, 0.4, 0.2)

    glPushMatrix()
    glTranslatef(x, y, z + height)
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), length / 2, length / 2, top_height, 20, 20)
    glPopMatrix()

    glPopMatrix()


def spawn_enemies():
    global enemies
    enemies = []

    enemy_types = [
        {'type': 'red', 'count': 2, 'scale': 2.0, 'health': 10},     # Big enemies - 3 hits
        {'type': 'purple', 'count': 2, 'scale': 0.7, 'health': 2},  # Small enemies - 1 hit
        {'type': 'yellow', 'count': 2, 'scale': 1.0, 'health': 5},  # Medium enemies - 2 hits
    ]

    # Spawn each type of enemy
    for enemy_type in enemy_types:
        for i in range(enemy_type['count']):
            # Random position across the map
            x = random.randint(-GRID_LENGTH - 500, GRID_LENGTH + 500)
            y = random.randint(-GRID_LENGTH - 500, GRID_LENGTH + 500)
            initial_angle = random.randint(0, 359)  # Random initial orientation

            # Avoid spawning in water
            tile_size = 50
            tile_x = (x // tile_size) * tile_size
            tile_y = (y // tile_size) * tile_size

            # If terrain map exists and position is water, adjust position
            if (tile_x, tile_y) in terrain_map and terrain_map[(tile_x, tile_y)] == 'water':
                x = random.randint(-GRID_LENGTH, GRID_LENGTH)
                y = random.randint(-GRID_LENGTH, GRID_LENGTH)

            # Store enemy with type, scale, angle and health information
            enemies.append((x, y, enemy_type['type'], enemy_type['scale'], initial_angle, enemy_type['health']))

# def spawn_barrels():
#     """Spawns 10 barrels at random positions across the terrain, ensuring they are far apart and not in water or mud."""
#     global explosive_drums, terrain_map
#     explosive_drums = []
#     min_distance = 500  # Minimum distance between barrels
#     tile_size = 50      # Tile size from terrain generation

#     attempts = 0
#     while len(explosive_drums) < 10 and attempts < 1000:  # Limit attempts to prevent infinite loop
#         attempts += 1
#         x = random.randint(-GRID_LENGTH * 7, GRID_LENGTH * 7)
#         y = random.randint(-GRID_LENGTH * 7, GRID_LENGTH * 7)

#         # Skip if too close to other barrels
#         if not all(math.hypot(x - bx, y - by) >= min_distance for bx, by in explosive_drums):
#             continue

#         # Find the nearest terrain tile
#         tile_x = (x // tile_size) * tile_size
#         tile_y = (y // tile_size) * tile_size

#         # Skip if in water or mud
#         if (tile_x, tile_y) in terrain_map and terrain_map[(tile_x, tile_y)] != 'grass':
#             continue

#         explosive_drums.append((x, y))


def move_enemies_towards_player():
    global player_health, player_dead, enemies

    if player_health == 0:
        return

    COLLISION_DIST = 35  # Base collision distance
    ROTATION_SPEED = 3   # Degrees per frame for enemy rotation

    for i in range(len(enemies)):
        # Extract enemy data by index instead of unpacking
        ex, ey = enemies[i][0], enemies[i][1]
        enemy_type = enemies[i][2]
        enemy_scale = enemies[i][3]

        # Get angle with default if not present
        enemy_angle = enemies[i][4] if len(enemies[i]) > 4 else 0

        # Get health with default if not present
        enemy_health = enemies[i][5] if len(enemies[i]) > 5 else 1

        px, py = player_pos
        dx, dy = px - ex, py - ey
        dist = math.hypot(dx, dy)

        # Calculate angle to player (in degrees)
        target_angle = (math.degrees(math.atan2(dy, dx)) - 90) % 360

        # Determine shortest rotation direction
        angle_diff = (target_angle - enemy_angle) % 360
        if angle_diff > 180:
            angle_diff -= 360

        # Rotate enemy toward player
        if abs(angle_diff) > ROTATION_SPEED:
            if angle_diff > 0:
                enemy_angle = (enemy_angle + ROTATION_SPEED) % 360
            else:
                enemy_angle = (enemy_angle - ROTATION_SPEED) % 360
        else:
            enemy_angle = target_angle

        # Move forward only when mostly facing the player
        move_speed = 0
        if abs(angle_diff) < 30:
            move_speed = enemy_speed

        # Calculate movement based on enemy's facing direction
        rad = math.radians(enemy_angle + 90)
        move_x = math.cos(rad) * move_speed
        move_y = math.sin(rad) * move_speed

        ex += move_x
        ey += move_y

        # Check collision with player
        if dist < COLLISION_DIST * enemy_scale and not player_dead:
            player_health -= 1
            if player_health <= 0:
                player_dead = True

        # Update enemy with new position, angle, and preserving health
        if len(enemies[i]) > 5:
            enemies[i] = (ex, ey, enemy_type, enemy_scale, enemy_angle, enemy_health)
        else:
            enemies[i] = (ex, ey, enemy_type, enemy_scale, enemy_angle)



def spawn_player_bullet():
    global player_pos, player_angle

    # Calculate direction vector based on player angle
    rad = math.radians(player_angle + 90)
    dir_x = math.cos(rad)  # Forward direction X
    dir_y = math.sin(rad)  # Forward direction Y

    # Calculate perpendicular vector (right side of player)
    right_x = math.cos(rad + math.pi/2)  # Right direction X
    right_y = math.sin(rad + math.pi/2)  # Right direction Y

    # Get base player position (center)
    base_x = player_pos[0]
    base_y = player_pos[1]

    # Gun dimensions based on LEGO model
    arm_offset = 19    # Distance arm extends from body
    arm_length = 19    # Length of the arm
    hand_offset = 6    # Hand to gun handle offset
    gun_barrel_y = 20  # Gun barrel length + position

    # Step 1: Move to right side of player (arm connection)
    gun_x = base_x + right_x * arm_offset
    gun_y = base_y + right_y * arm_offset

    # Step 2: Move out along arm length
    gun_x += -right_x * arm_length  # Negative because gun extends opposite to right vector
    gun_y += -right_y * arm_length

    # Step 3: Add offset for hand and gun handle
    gun_x += -right_x * hand_offset
    gun_y += -right_y * hand_offset

    # Step 4: Add forward offset for gun barrel
    gun_x += dir_x * gun_barrel_y
    gun_y += dir_y * gun_barrel_y

    # Create bullet at calculated gun tip position
    bullets.append([gun_x, gun_y, player_angle, BULLET_LIFE])



def shrink_expand():
    global enemy_scale_factor, enemy_scale_direction, player_angle
    global cheat_cooldown
    enemy_scale_factor += 0.005 * enemy_scale_direction
    if enemy_scale_factor >= 1.2:
        enemy_scale_factor = 1.2
        enemy_scale_direction = -1
    elif enemy_scale_factor <= 0.8:
        enemy_scale_factor = 0.8
        enemy_scale_direction = 1


def animate():
    global enemy_scale_factor, enemy_scale_direction, fire_cooldown, enemy_respawn_timer

    if player_dead:
        glutPostRedisplay()
        return

    if left_mouse_pressed and not player_dead:
        if fire_cooldown <= 0:
            spawn_player_bullet()
            fire_cooldown = FIRE_RATE
        else:
            fire_cooldown -= 1

    shrink_expand()
    process_movement()
    move_enemies_towards_player()
    update_bullets()
    check_enemy_respawn()  # Add this line to check for enemy respawning
    glutPostRedisplay()


def draw_text(x, y, text, font=GLUT_BITMAP_9_BY_15):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def setupCamera():
    global player_pos, player_angle

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1000/800, 0.1, 15000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Chase camera parameters
    cam_distance = 150  # Distance behind player
    cam_height = 120    # Height above player

    # Calculate camera position based on player angle
    rad = math.radians(player_angle + 90)  # Player's facing angle

    # Position camera behind player
    camera_x = player_pos[0] - math.cos(rad) * cam_distance
    camera_y = player_pos[1] - math.sin(rad) * cam_distance
    camera_z = HEAD_HEIGHT + cam_height  # Above player

    # Calculate look-at point (slightly ahead of player)
    look_distance = 100  # Distance ahead to look
    look_x = player_pos[0] + math.cos(rad) * look_distance
    look_y = player_pos[1] + math.sin(rad) * look_distance
    look_z = HEAD_HEIGHT  # At player's head level

    # Set up the camera
    gluLookAt(camera_x, camera_y, camera_z,  # Camera position
              look_x, look_y, look_z,        # Look at point
              0, 0, 1)                       # Up vector (Z is up)

def update_bullets():
        global bullets, enemies, score, missed_bullets, player_health, player_dead, orange_screen_flag, crates
        keep_list = []

        for b in bullets:
            x = b[0]
            y = b[1]
            ang = b[2]
            life = b[3]
            rad = math.radians(ang + 90)
            x = x + BULLET_SPEED * math.cos(rad)
            y = y + BULLET_SPEED * math.sin(rad)
            life = life - 1

            hit_enemy = False
            j = 0
            while j < len(enemies):
                ex, ey = enemies[j][0], enemies[j][1]
                enemy_type = enemies[j][2]
                enemy_scale = enemies[j][3]
                enemy_angle = enemies[j][4] if len(enemies[j]) > 4 else 0
                enemy_health = enemies[j][5] if len(enemies[j]) > 5 else 1

                # Check for collision with enemy
                if math.hypot(ex - x, ey - y) < 45 * enemy_scale:
                    hit_enemy = True
                    # Reduce enemy health
                    enemy_health -= 1

                    if enemy_health <= 0:
                        # Enemy is dead when health reaches 0
                        enemies.pop(j)
                        # Add score based on enemy type
                        if enemy_type == 'red':  # Big enemy
                            score += 3
                        elif enemy_type == 'yellow':  # Medium enemy
                            score += 2
                        else:  # Small enemy (purple)
                            score += 1
                    else:
                        # Update enemy with reduced health
                        enemies[j] = (ex, ey, enemy_type, enemy_scale, enemy_angle, enemy_health)
                        j += 1
                    break
                else:
                    j += 1

            # Process barrel collisions
            for i in range(len(explosive_drums) - 1, -1, -1):
                ex, ey = explosive_drums[i]
                if math.hypot(ex - x, ey - y) < 30:
                    explosive_drums.pop(i)
                    hit_enemy = True
                    score += 5
                    orange_screen_flag = True
                    # Damage nearby enemies from explosion
                    for j in range(len(enemies) - 1, -1, -1):
                        ex2, ey2 = enemies[j][0], enemies[j][1]
                        if math.hypot(ex2 - ex, ey2 - ey) < 300:
                            enemies.pop(j)
                            score += 2
                    break

            p=0
            while p < len(crates):
                crate_pos = crates[p]
                crate_x = crate_pos[0]
                crate_y = crate_pos[1]
                if math.hypot(x - crate_x, y - crate_y) < 50:
                    cx = 5000
                    cy = 5000
                    crates[p]=(cx,cy)
                    hit_enemy = True
                    print("crate hit!",crates[p])
                
                
                p = p + 1

            # Add bullet to keep_list if it hasn't hit anything and still has life
            if not hit_enemy and life > 0:
                keep_list.append([x, y, ang, life])
            elif not hit_enemy and life <= 0:
                missed_bullets += 1

        bullets = keep_list


def draw_sphere(x, y, z, radius, color):
    if color == "green":
        glPushMatrix()
        glTranslatef(x, y, z)  # Position the sphere at (x, y, z)

        glColor3f(0.0, 1.0, 0.0)  # Set the color to green

        # Draw the sphere using gluSphere (with the specified radius)
        gluSphere(gluNewQuadric(), radius, 20, 20)

        glPopMatrix()

    elif color == "gold":
        glPushMatrix()
        glTranslatef(x, y, z)  # Position the sphere at (x, y, z)

        glColor3f(1.0, 0.84, 0.0)  # Set the color to green

        # Draw the sphere using gluSphere (with the specified radius)
        gluSphere(gluNewQuadric(), radius, 20, 20)

        glPopMatrix()


def draw_room(x, y, width, depth, height, door_width=100, door_height=150):
    """Draws a large open-top room (4 walls, no ceiling or floor) with an open door on the front wall, and a floor."""
    glColor3f(0.5, 0.5, 0.5)  # Wall color (light brown)
    room_size=500
    # Left wall
    glBegin(GL_QUADS)
    glVertex3f(x, y, 0)
    glVertex3f(x, y, height)
    glVertex3f(x, y + depth, height)
    glVertex3f(x, y + depth, 0)
    glEnd()

    # Right wall
    glBegin(GL_QUADS)
    glVertex3f(x + width, y, 0)
    glVertex3f(x + width, y, height)
    glVertex3f(x + width, y + depth, height)
    glVertex3f(x + width, y + depth, 0)
    glEnd()

    # Back wall
    glBegin(GL_QUADS)
    glVertex3f(x, y + depth, 0)
    glVertex3f(x + width, y + depth, 0)
    glVertex3f(x + width, y + depth, height)
    glVertex3f(x, y + depth, height)
    glEnd()

    # Front wall with open door
    glBegin(GL_QUADS)
    # Bottom-left (door gap starts here)
    glVertex3f(x, y, 0)
    # Bottom-right of the wall before the door
    glVertex3f(x + width - door_width, y, 0)
    # Top-right of the wall before the door
    glVertex3f(x + width - door_width, y, height)
    # Top-left of the wall before the door
    glVertex3f(x, y, height)
    glEnd()

    # Now, draw the open door (gap in the front wall)
    glColor3f(1, 1, 1)  # White or transparent area for the door

    # The open door (gap)
    glBegin(GL_QUADS)
    # Bottom-left of the door
    glVertex3f(x + width - door_width, y, 0)
    # Bottom-right of the door
    glVertex3f(x + width, y, 0)
    # Top-right of the door
    glVertex3f(x + width, y, door_height)
    # Top-left of the door
    glVertex3f(x + width - door_width, y, door_height)
    glEnd()

    # === Draw the floor ===
    glColor3f(0.662, 0.662, 0.662)  # Floor color (wood-like)

    glBegin(GL_QUADS)
    # Bottom-left of the floor
    glVertex3f(x, y, 1)
    # Bottom-right of the floor
    glVertex3f(x + width, y, 1)
    # Top-right of the floor
    glVertex3f(x + width, y + depth, 1)
    # Top-left of the floor
    glVertex3f(x, y + depth, 1)
    glEnd()

    # Back wall
    glBegin(GL_QUADS)
    glVertex3f(x, y + depth, 0)
    glVertex3f(x + width, y + depth, 0)
    glVertex3f(x + width, y + depth, height)
    glVertex3f(x, y + depth, height)
    glEnd()

    # Front wall with open door
    glBegin(GL_QUADS)
    # Bottom-left (door gap starts here)
    glVertex3f(x, y, 0)
    # Bottom-right of the wall before the door
    glVertex3f(x + width - door_width, y, 0)
    # Top-right of the wall before the door
    glVertex3f(x + width - door_width, y, height)
    # Top-left of the wall before the door
    glVertex3f(x, y, height)
    glEnd()

    # Now, draw the open door (gap in the front wall)
    glColor3f(1, 1, 1)  # White or transparent area for the door

    # The open door (gap)
    glBegin(GL_QUADS)
    # Bottom-left of the door
    glVertex3f(x + width - door_width, y, 0)
    # Bottom-right of the door
    glVertex3f(x + width, y, 0)
    # Top-right of the door
    glVertex3f(x + width, y, door_height)
    # Top-left of the door
    glVertex3f(x + width - door_width, y, door_height)
    glEnd()


def draw_crate(x, y, z=0):
    """Draws a simple crate at position (x, y, z)."""
    crate_size = 100  # Size of the crate

    # Crate color (brownish color)
    glColor3f(199 / 255, 157 / 255, 122 / 255)

    glPushMatrix()
    glTranslatef(x, y, z)  # Position the crate

    # Draw the crate (simple cube)
    glBegin(GL_QUADS)

    # Front face
    glVertex3f(-crate_size / 2, -crate_size / 2, crate_size / 2)
    glVertex3f(crate_size / 2, -crate_size / 2, crate_size / 2)
    glVertex3f(crate_size / 2, crate_size / 2, crate_size / 2)
    glVertex3f(-crate_size / 2, crate_size / 2, crate_size / 2)

    # Back face
    glVertex3f(-crate_size / 2, -crate_size / 2, -crate_size / 2)
    glVertex3f(crate_size / 2, -crate_size / 2, -crate_size / 2)
    glVertex3f(crate_size / 2, crate_size / 2, -crate_size / 2)
    glVertex3f(-crate_size / 2, crate_size / 2, -crate_size / 2)

    # Left face
    glVertex3f(-crate_size / 2, -crate_size / 2, crate_size / 2)
    glVertex3f(-crate_size / 2, -crate_size / 2, -crate_size / 2)
    glVertex3f(-crate_size / 2, crate_size / 2, -crate_size / 2)
    glVertex3f(-crate_size / 2, crate_size / 2, crate_size / 2)

    # Right face
    glVertex3f(crate_size / 2, -crate_size / 2, crate_size / 2)
    glVertex3f(crate_size / 2, -crate_size / 2, -crate_size / 2)
    glVertex3f(crate_size / 2, crate_size / 2, -crate_size / 2)
    glVertex3f(crate_size / 2, crate_size / 2, crate_size / 2)

    # Top face
    glVertex3f(-crate_size / 2, crate_size / 2, crate_size / 2)
    glVertex3f(crate_size / 2, crate_size / 2, crate_size / 2)
    glVertex3f(crate_size / 2, crate_size / 2, -crate_size / 2)
    glVertex3f(-crate_size / 2, crate_size / 2, -crate_size / 2)

    # Bottom face
    glVertex3f(-crate_size / 2, -crate_size / 2, crate_size / 2)
    glVertex3f(crate_size / 2, -crate_size / 2, crate_size / 2)
    glVertex3f(crate_size / 2, -crate_size / 2, -crate_size / 2)
    glVertex3f(-crate_size / 2, -crate_size / 2, -crate_size / 2)

    glEnd()
    glPopMatrix()


def draw_explosive_drum(x, y, z=0):
    """Draws an explosive drum (barrel) at position (x, y, z)."""
    radius = 30  # Radius of the drum
    height = 90  # Height of the drum

    # Drum color (red with a black top and bottom)
    glColor3f(1.0, 0.0, 0.0)  # Red color for the barrel

    # Draw the barrel body (cylinder)
    glPushMatrix()
    glTranslatef(x, y, z)  # Position the barrel

    # Draw the side of the drum (cylinder)
    gluCylinder(gluNewQuadric(), radius, radius, height, 20, 20)

    # Draw the top of the drum (circle)
    glPushMatrix()
    glTranslatef(0, 0, height / 2)  # Position the top cap
    glColor3f(0.0, 0.0, 0.0)  # Black color for the top and bottom
    gluDisk(gluNewQuadric(), 0, radius, 20, 20)  # Draw the top cap
    glPopMatrix()

    # Draw the bottom of the drum (circle)
    glPushMatrix()
    glTranslatef(0, 0, -height / 2)  # Position the bottom cap
    glColor3f(0.0, 0.0, 0.0)  # Black color for the top and bottom
    gluDisk(gluNewQuadric(), 0, radius, 20, 20)  # Draw the bottom cap
    glPopMatrix()

    glPopMatrix()


def draw_walls():
    wall_height = 50

    # === Existing boundary walls (keep this) ===
    # ... (your current bounding room walls)

    # === Add 3 larger rooms with open ceilings ===
    room_width = 900
    room_depth = 900

    # Room 1 (Top-left)
    draw_room(-1500, 400, 900, 900, 250, door_width=100, door_height=150)

    # Room 2 (Center)
    draw_room(-1500, -1100, 900, 900, 250, door_width=100, door_height=150)

    # Room 3 (Bottom-right)
    draw_room(800, -1100, 900, 900, 250, door_width=100, door_height=150)

    draw_room(-1800, 2500, 1500, 1500, 250, door_width=100, door_height=150)

    # === Create Open Doors on the Rooms ===
    # Room 1 (Open door on the front wall)
    # Change color to create door-like appearance

    glBegin(GL_QUADS)
    # Open door on the front wall
    glVertex3f(-800, 400, 50)  # Bottom-left
    glVertex3f(-800 + 100, 400, 50)  # Bottom-right (door)
    glVertex3f(-800 + 100, 400, 50)  # Top-right (door)
    glVertex3f(-800, 400, 60)  # Top-left
    glEnd()
    # === Add Crates Inside the Rooms ===
    # Add crates to each room


def generate_terrain():
    """Generates terrain with grass, fixed pond, trees, and smooth muddy paths."""
    global terrain_map, tree_positions
    tile_size = 50
    grid_multiplier = 7
    grid_range = GRID_LENGTH * grid_multiplier
    tree_positions.clear()

    terrain_map = {}

    # === FIXED POND POSITION ===
    pond_size = 300
    pond_origin_x = 400
    pond_origin_y = 200

    pond_tiles = set()
    for i in range(pond_origin_x, pond_origin_x + pond_size * tile_size, tile_size):
        for j in range(pond_origin_y, pond_origin_y + pond_size * tile_size, tile_size):
            pond_tiles.add((i, j))

    # === Define Mud Paths ===
    path_width = 2  # Number of tiles wide
    horizontal_mud_y = 0  # Y position of horizontal path (middle)
    vertical_mud_x = 100  # X position of vertical path

    def is_on_horizontal_path(j):
        return horizontal_mud_y - path_width * tile_size <= j <= horizontal_mud_y + path_width * tile_size

    def is_on_vertical_path(i):
        return vertical_mud_x - path_width * tile_size <= i <= vertical_mud_x + path_width * tile_size

    for i in range(-grid_range, grid_range, tile_size):
        for j in range(-grid_range, grid_range, tile_size):
            pos = (i, j)

            if pos in pond_tiles:
                terrain_type = 'water'
            elif is_on_horizontal_path(j) or is_on_vertical_path(i):
                terrain_type = 'mud'  # Smooth mud road
            else:
                terrain_type = 'grass'
                if random.random() < 0.02:
                    tree_positions.append((i + tile_size // 2, j + tile_size // 2))

            terrain_map[pos] = terrain_type


def draw_bullets():
    glColor3f(1, 0, 0)
    for x, y, i, j in bullets:
        glPushMatrix()
        glTranslatef(x, y, BULLET_SIZE / 2)
        glutSolidCube(BULLET_SIZE)
        glPopMatrix()


def draw_enemy(enemy_type='red', enemy_scale=1.0, angle=0):
    """Draws an enemy with angry Lego-style design."""
    # Set color based on enemy type
    if enemy_type == 'red':
        body_color = (1.0, 0.0, 0.0)  # Red
    elif enemy_type == 'purple':
        body_color = (0.8, 0.0, 0.8)  # Purple
    elif enemy_type == 'yellow':
        body_color = (1.0, 1.0, 0.0)  # Yellow
    else:
        body_color = (1.0, 0.0, 0.0)  # Default red

    # Apply the proper scale
    final_scale = enemy_scale * enemy_scale_factor

    glPushMatrix()
    # Apply rotation to face correct direction
    glRotatef(angle, 0, 0, 1)
    glScalef(final_scale, final_scale, final_scale)

    # Rest of the drawing code remains the same...

        # === LEGO Minifigure Enemy ===

        # Legs
    leg_width = 12
    leg_height = 30
    leg_spacing = 3

    # Left Leg
    glPushMatrix()
    glColor3f(*body_color)
    glTranslatef(-leg_width / 2 - leg_spacing / 2, 0, 0)
    glScalef(leg_width, 10, leg_height)
    glutSolidCube(1)
    glPopMatrix()

    # Right Leg
    glPushMatrix()
    glColor3f(*body_color)
    glTranslatef(leg_width / 2 + leg_spacing / 2, 0, 0)
    glScalef(leg_width, 10, leg_height)
    glutSolidCube(1)
    glPopMatrix()

    # Hip connector
    glPushMatrix()
    glColor3f(*body_color)
    glTranslatef(0, 0, leg_height)
    glScalef(leg_width * 2 + leg_spacing, 10, 5)
    glutSolidCube(1)
    glPopMatrix()

    # Torso (LEGO minifigure style)
    torso_height = 36
    glPushMatrix()
    glColor3f(*body_color)
    glTranslatef(0, 0, leg_height + torso_height / 2)

    # Main torso block
    glPushMatrix()
    glScalef(27, 15, torso_height)
    glutSolidCube(1)
    glPopMatrix()

    # Evil logo on chest
    glPushMatrix()
    glColor3f(0.0, 0.0, 0.0)  # Black logo
    glTranslatef(0, 7.6, 0)
    glScalef(12, 0.5, 12)
    glutSolidCube(1)
    glPopMatrix()

    glPopMatrix()  # End of torso

    # Head (LEGO cylinder-like head)
    glPushMatrix()
    glColor3f(1, 0.8, 0.6)  # Skin color
    glTranslatef(0, 0, leg_height + torso_height + 10)

    # LEGO head is cylindrical with rounded top
    gluCylinder(gluNewQuadric(), 15, 15, 17, 20, 5)
    glTranslatef(0, 0, 17)
    glutSolidSphere(15, 20, 20)

    # Angry face features
    glColor3f(0, 0, 0)

    # Angry eyebrows
    glPushMatrix()
    glTranslatef(-5, 13, -5)  # Left eyebrow
    glRotatef(-30, 0, 0, 1)
    glScalef(7, 1.5, 1.5)
    glutSolidCube(1)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(5, 13, -5)  # Right eyebrow
    glRotatef(30, 0, 0, 1)
    glScalef(7, 1.5, 1.5)
    glutSolidCube(1)
    glPopMatrix()

    # Eyes (angry looking)
    glPushMatrix()
    glTranslatef(5, 13, -9)
    glutSolidSphere(2.5, 8, 8)
    glTranslatef(-10, 0, 0)
    glutSolidSphere(2.5, 8, 8)
    glPopMatrix()

    # Frown (angry mouth)
    glPushMatrix()
    glTranslatef(0, 10, -15)
    glRotatef(180, 0, 0, 1)  # Rotate to make it a frown
    glScalef(10, 1.5, 1.5)
    glutSolidCube(1)
    glPopMatrix()

    glPopMatrix()  # End of head

    # Arms
    arm_length = 19

    # Left arm
    glPushMatrix()
    glColor3f(*body_color)
    glTranslatef(-19, 0, leg_height + torso_height - 6)
    glRotatef(90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 5, 5, arm_length, 8, 8)

    # Left hand
    glColor3f(1, 0.8, 0.6)  # Skin color hands
    glTranslatef(0, 0, arm_length)
    glutSolidSphere(6, 8, 8)
    glPopMatrix()

    # Right arm
    glPushMatrix()
    glColor3f(*body_color)
    glTranslatef(19, 0, leg_height + torso_height - 6)
    glRotatef(-90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 5, 5, arm_length, 8, 8)

    # Right hand
    glColor3f(1, 0.8, 0.6)  # Skin color hands
    glTranslatef(0, 0, arm_length)
    glutSolidSphere(6, 8, 8)
    glPopMatrix()

    glPopMatrix()


def draw_tree(x, y, z=0):
    """Draws a simple tree at position (x, y, z)."""

    trunk_height = 200  # Height of the tree trunk
    trunk_radius = 10  # Radius of the trunk
    crown_radius = 50  # Radius of the tree crown (leaves)

    # Draw the tree trunk (cylinder)
    glPushMatrix()
    glTranslatef(x, y, z)  # Position the tree at (x, y, z)
    glColor3f(0.6, 0, 0.1)  # Brown color for the trunk
    gluCylinder(gluNewQuadric(), trunk_radius, trunk_radius, trunk_height, 20, 20)  # Draw the trunk
    glPopMatrix()

    # Draw the tree crown (leaves) using spheres
    # First sphere at the top of the trunk
    glPushMatrix()
    glTranslatef(x, y, z + trunk_height)  # Position the first crown sphere above the trunk
    glColor3f(0.0, 0.8, 0.0)  # Green color for the leaves
    glutSolidSphere(crown_radius, 20, 20)  # Draw the first crown sphere
    glPopMatrix()

    # Second sphere for additional crown
    glPushMatrix()
    glTranslatef(x, y, z + trunk_height + 3)  # Position the second crown sphere higher
    glColor3f(0.0, 0.8, 0.0)  # Green color for the leaves
    glutSolidSphere(crown_radius * 0.8, 20, 20)  # Draw the second crown sphere (smaller)
    glPopMatrix()

    # Third sphere for additional crown
    glPushMatrix()
    glTranslatef(x, y, z + trunk_height + 5)  # Position the third crown sphere higher
    glColor3f(0.0, 0.8, 0.0)  # Green color for the leaves
    glutSolidSphere(crown_radius * 0.6, 20, 20)  # Draw the third crown sphere (smaller)
    glPopMatrix()


def draw_player():
    glPushMatrix()

    if player_dead:
        glRotatef(-90, 1, 0, 0)  # Fallen player
    glTranslatef(0, -25, 0)

    # === LEGO Minifigure Character (Scaled up) ===

    # Legs
    leg_width = 12  # Increased from 10
    leg_height = 30  # Increased from 25
    leg_spacing = 3  # Increased from 2

    # Left Leg
    glPushMatrix()
    glColor3f(0, 0, 0.7)  # Dark blue legs
    glTranslatef(-leg_width / 2 - leg_spacing / 2, 0, 0)
    glScalef(leg_width, 10, leg_height)  # Increased from 8
    glutSolidCube(1)
    glPopMatrix()

    # Right Leg
    glPushMatrix()
    glColor3f(0, 0, 0.7)  # Dark blue legs
    glTranslatef(leg_width / 2 + leg_spacing / 2, 0, 0)
    glScalef(leg_width, 10, leg_height)  # Increased from 8
    glutSolidCube(1)
    glPopMatrix()

    # Hip connector
    glPushMatrix()
    glColor3f(0, 0, 0.8)
    glTranslatef(0, 0, leg_height)
    glScalef(leg_width * 2 + leg_spacing, 10, 5)  # Increased from 8, 4
    glutSolidCube(1)
    glPopMatrix()

    # Torso (LEGO minifigure style)
    torso_height = 36  # Increased from 30
    glPushMatrix()
    glColor3f(0, 0, 1)  # Blue torso
    glTranslatef(0, 0, leg_height + torso_height / 2)

    # Main torso block
    glPushMatrix()
    glScalef(27, 15, torso_height)  # Increased from 22, 12, 30
    glutSolidCube(1)
    glPopMatrix()

    # LEGO logo on chest
    glPushMatrix()
    glColor3f(1, 0, 0)  # Red logo
    glTranslatef(0, 7.6, 0)  # Increased from 6.1
    glScalef(12, 0.5, 12)  # Increased from 10
    glutSolidCube(1)
    glPopMatrix()

    glPopMatrix()  # End of torso

    # Head (LEGO cylinder-like head)
    glPushMatrix()
    glColor3f(1, 0.8, 0.6)  # Skin color
    glTranslatef(0, 0, leg_height + torso_height + 10)  # Adjusted for bigger head

    # LEGO head is cylindrical with rounded top
    gluCylinder(gluNewQuadric(), 15, 15, 17, 20, 5)  # Increased from 12, 14
    glTranslatef(0, 0, 17)
    glutSolidSphere(15, 20, 20)  # Increased from 12

    # Face features
    glColor3f(0, 0, 0)
    # Eyes
    glPushMatrix()
    glTranslatef(5, 13, -9)  # Adjusted position
    glutSolidSphere(2.5, 8, 8)  # Slightly larger eyes
    glTranslatef(-10, 0, 0)
    glutSolidSphere(2.5, 8, 8)
    glPopMatrix()

    # Smile
    glPushMatrix()
    glTranslatef(0, 10, -15)  # Adjusted position
    glScalef(10, 1.5, 1.5)  # Wider smile
    glutSolidCube(1)
    glPopMatrix()

    glPopMatrix()  # End of head

    # Arms
    arm_length = 19  # Increased from 15

    # Left arm
    glPushMatrix()
    glColor3f(0, 0, 1)  # Blue arm
    glTranslatef(-19, 0, leg_height + torso_height - 6)  # Adjusted position
    glRotatef(90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 5, 5, arm_length, 8, 8)  # Increased from 4

    # Left hand
    glColor3f(1, 1, 0)  # Yellow LEGO hands
    glTranslatef(0, 0, arm_length)
    glutSolidSphere(6, 8, 8)  # Increased from 5
    glPopMatrix()

    # Right arm with gun
    glPushMatrix()
    glColor3f(0, 0, 1)  # Blue arm
    glTranslatef(19, 0, leg_height + torso_height - 6)  # Adjusted position
    glRotatef(-90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 5, 5, arm_length, 8, 8)  # Increased from 4

    # Right hand
    glColor3f(1, 1, 0)  # Yellow LEGO hands
    glTranslatef(0, 0, arm_length)
    glutSolidSphere(6, 8, 8)  # Increased from 5

    # Gun (held by right hand)
    glPushMatrix()
    glColor3f(0.2, 0.2, 0.2)  # Dark gray gun
    glTranslatef(6, 10, 0)  # Adjusted position

    # Gun handle
    glPushMatrix()
    glScalef(4, 12, 4)  # Increased from 3, 10, 3
    glutSolidCube(1)
    glPopMatrix()

    # Gun barrel
    glPushMatrix()
    glTranslatef(0, 10, 0)  # Adjusted position
    glScalef(6, 18, 6)  # Increased from 5, 15, 5
    glutSolidCube(1)
    glPopMatrix()

    # Gun sight
    glPushMatrix()
    glColor3f(1, 0, 0)  # Red sight
    glTranslatef(0, 20, 0)  # Adjusted position
    glutSolidSphere(2, 8, 8)  # Increased from 1.5
    glPopMatrix()

    glPopMatrix()  # End of gun

    glPopMatrix()  # End of right arm

    glPopMatrix()  # End of player}


def if_dead():
    global cheat_cooldown, cam_mode, player_pos, player_angle, player_health, player_dead
    global missed_bullets, score, gun_follow, player_key

    player_dead = False
    player_pos[:] = [0, 0]
    player_health = 7
    player_key = 0
    missed_bullets = 0
    score = 0
    bullets.clear()
    cheat_cooldown = 0
    spawn_enemies()
    return



def keyboardListener(key, x, y):
    global player_pos, player_angle, player_health, player_dead, orange_screen_flag
    global missed_bullets, score, key_states

    if player_dead:
        if key in (b'r', b'R'):
            if_dead()
        return

    if key in (b'q', b'Q') and orange_screen_flag:
        orange_screen_flag = False

    # Track key states
    if key in key_states:
        key_states[key] = True

    glutPostRedisplay()

def keyboardUpListener(key, x, y):
    global key_states

    if key in key_states:
        key_states[key] = False

    glutPostRedisplay()

def process_movement():
    global player_pos, player_angle, orange_screen_flag

    move_speed = 20

    # Handle rotation
    if key_states[b'a'] and not key_states[b'd'] and not key_states[b'w'] and not key_states[b's']:
        # Rotate only if not moving
        player_angle = (player_angle + 5) % 360
    elif key_states[b'd'] and not key_states[b'a'] and not key_states[b'w'] and not key_states[b's']:
        # Rotate only if not moving
        player_angle = (player_angle - 5) % 360

    # Calculate forward and right vectors
    forward_angle = player_angle + 90
    right_angle = player_angle

    # Calculate movement direction based on key combinations
    move_angle = None
    if key_states[b'w'] and not key_states[b's']:

        if key_states[b'a'] and not key_states[b'd']:
            # Forward-left (diagonal)
            move_angle = forward_angle + 45
        elif key_states[b'd'] and not key_states[b'a']:
            # Forward-right (diagonal)
            move_angle = forward_angle - 45
        else:
            # Forward
           
            move_angle = forward_angle
    elif key_states[b's'] and not key_states[b'w']:
        if key_states[b'a'] and not key_states[b'd']:
            move_angle = forward_angle + 135
        elif key_states[b'd'] and not key_states[b'a']:
            move_angle = forward_angle - 135
        else:
            # Backward
            move_angle = forward_angle - 180

    if move_angle is not None:

        if is_colliding_with_objects(player_pos[0],player_pos[1]):
            rad = math.radians(move_angle)
            dx = math.cos(rad) * move_speed
            dy = math.sin(rad) * move_speed
        
        # Check for collision in the direction of movement and block
            if abs(player_pos[0] + dx) < player_pos[0] and abs(player_pos[1] + dy) < player_pos[1]:
                player_pos[0] += 50  # Move player back by 50 on X-axis
                player_pos[1] += 50  # Move player back by 50 on Y-axis
            elif abs(player_pos[0] + dx) > player_pos[0] and abs(player_pos[1] + dy) > player_pos[1]:
                player_pos[0] -= 50  # Move player back by 50 on X-axis
                player_pos[1] -= 50  # Move player back by 50 on Y-axis
            elif abs(player_pos[0] + dx) > player_pos[0] and abs(player_pos[1] + dy) < player_pos[1]:
                player_pos[0] -= 50  # Move player back by 50 on X-axis
                player_pos[1] += 50  # Move player back by 50 on Y-axis
            elif abs(player_pos[0] + dx) < player_pos[0] and abs(player_pos[1] + dy) > player_pos[1]:
                player_pos[0] += 50  # Move player back by 50 on X-axis
                player_pos[1] -= 50  # Move player back by 50 on Y-axis

        else:
            rad = math.radians(move_angle)
            dx = math.cos(rad) * move_speed
            dy = math.sin(rad) * move_speed
            player_pos[0] += dx
            player_pos[1] += dy
            orange_screen_flag = False


def specialKeyListener(key, x, y):
    global cam_angle, cam_elev
    if key == GLUT_KEY_LEFT:
        cam_angle = (cam_angle - 2) % 360
    elif key == GLUT_KEY_RIGHT:
        cam_angle = (cam_angle + 2) % 360
    elif key == GLUT_KEY_UP:
        cam_elev = min(cam_elev + 2, MAX_ELEV_DEG)
    elif key == GLUT_KEY_DOWN:
        cam_elev = max(cam_elev - 2, MIN_ELEV_DEG)
    glutPostRedisplay()


def mouseListener(button, state, x, y):
    global left_mouse_pressed

    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            left_mouse_pressed = True
            spawn_player_bullet()
        else:
            left_mouse_pressed = False

    glutPostRedisplay()


def showScreen():
    global score, player_health, explosive_drums, orange_screen_flag, health_packs, player_key
    rotation_angle = 0
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    setupCamera()
    draw_bullets()

    glPushMatrix()
    glRotatef(rotation_angle, 0.0, 1.0, 0.0)

    glPopMatrix()

    rotation_angle += 0.1
    if rotation_angle > 360:
        rotation_angle -= 360
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], 1)
    glRotatef(player_angle, 0, 0, 1)
    draw_player()

    glPopMatrix()

    draw_walls()
    for x in explosive_drums:
        drum_pos_x = x[0]
        drum_pos_y = x[1]
        drum_pos_z = 0
        draw_explosive_drum(drum_pos_x, drum_pos_y, drum_pos_z)

    for c in crates:
        c_pos_x = c[0]
        c_pos_y = c[1]
        c_pos_z = 50
        draw_crate(c_pos_x, c_pos_y, c_pos_z)

    for g in range(len(health_packs) - 1):

        if abs(player_pos[0] - health_packs[g][0]) < 15 and abs(player_pos[1] - health_packs[g][1]) < 15:
            player_health += 2
            del health_packs[g]

        else:
            draw_sphere(health_packs[g][0], health_packs[g][1], 70, 25, "green")

    for key in range(len(keys)):

        if abs(player_pos[0] - keys[key][0]) < 15 and abs(player_pos[1] - keys[key][1]) < 15:
            player_key += 1
            del keys[key]

        else:
            draw_sphere(keys[key][0], keys[key][1], 70, 8, "gold")

    tile_size = 50
    draw_tree(300, -250, 0)
    val_x = 300
    val_y = -250
    c_x = -100
    c_y = -250
    g_x = -100
    g_y = 300
    r_x = 283.1811161232042 + 350
    r_y = 188.05407289332277
    for i in range(10):
        draw_tree(r_x, r_y, 0)
        r_x += 350
    for i in range(17):
        draw_tree(val_x, g_y, 0)
        g_y += 300

    for i in range(10):
        draw_tree(val_x, val_y, 0)
        val_y -= 300

    for i in range(10):
        draw_tree(c_x, c_y, 0)
        c_y -= 300

    if orange_screen_flag:
        glColor3f(1.0, 0.647, 0.0)
        glBegin(GL_QUADS)
        glVertex2f(-5000, -5000)
        glVertex2f(5000, -5000)
        glVertex2f(5000, 5000)
        glVertex2f(-5000, 5000)
        glEnd()

    for (i, j), terrain_type in terrain_map.items():
        if terrain_type == 'grass':
            glColor3f(0.0, 0.6, 0.0)  # Green
        elif terrain_type == 'mud':
            glColor3f(0.55, 0.27, 0.07)  # Brown
        elif terrain_type == 'water':
            glColor3f(0.0, 0.4, 0.7)  # Blue

        glBegin(GL_QUADS)
        glVertex3f(i, j, 0)
        glVertex3f(i + tile_size, j, 0)
        glVertex3f(i + tile_size, j + tile_size, 0)
        glVertex3f(i, j + tile_size, 0)
        glEnd()


    for enemy_pos in enemies:
        if player_dead:
            break

        if len(enemy_pos) < 5:
            ex, ey, enemy_type, enemy_scale = enemy_pos
            enemy_angle = 0  # Default angle
        else:
            ex, ey, enemy_type, enemy_scale = enemy_pos[:4]
            enemy_angle = enemy_pos[4] if len(enemy_pos) > 4 else 0

        glPushMatrix()
        glTranslatef(ex, ey, 0)
        draw_enemy(enemy_type, enemy_scale, enemy_angle)
        glPopMatrix()


    draw_text(10, 770, f"Player Life Remaining: {player_health}")
    if player_dead:
        draw_text(10, 740, "GAME OVER!!! press R to restart")
        draw_text(10, 710, " ")
    else:
        draw_text(10, 740, f"Game Score: {score}")
        draw_text(10, 710, f"Player Bullet Missed: {missed_bullets}")
        draw_text(10, 680, f"Keys Found: {player_key}")
    glutSwapBuffers()


def main():
    global enemy_respawn_timer
    glutInit()
    generate_terrain()
    #spawn_barrels()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(300, 100)
    glutCreateWindow(b"Boom!!!!")
    glEnable(GL_DEPTH_TEST)
    spawn_enemies()
    enemy_respawn_timer = ENEMY_RESPAWN_DELAY  # Add this line
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutKeyboardUpFunc(keyboardUpListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(animate)
    glutMainLoop()


if __name__ == "__main__":
    main()
