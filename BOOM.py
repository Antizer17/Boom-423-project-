from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math
room1_x, room1_y, room1_width, room1_depth = -1500, 400, 900, 900
room2_x, room2_y, room2_width, room2_depth = -1500, -1100, 900, 900
room3_x, room3_y, room3_width, room3_depth = 800, -1100, 900, 900

room4_x, room4_y, room4_width, room4_depth = -1800, 2500, 1500, 1500
orange_screen_flag=False
explosive_drums=[(-1100, 50),(-1400, -400),(100, 100)]
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

health_packs=[    (-663.312606397818, 1200.4214978749658, 70,25),
    (-1360.821003117057, 568.3919648628456, 70,25),
    (-863.312606397818, 1200.4214978749658, 70,25)]

keys=[(-1360, 768.3919648628456, 70)]

scaling_factor=1
gun_rotation=0
game_over=True
enemy2_pos=[0,0]
terrain_map = {}
tree_positions = []  
cam_radius = 600
cam_angle = 0
cam_height = 600
cam_elev = 50
MIN_ELEV_DEG = 15
MAX_ELEV_DEG = 80
fovY = 105

cam_mode = "tp"
BACK_OFFSET = 40
LOOK_DISTANCE = 100
HEAD_HEIGHT = 145

cheat_mode = False
SPIN_SPEED_DEG = 7
cheat_cam_angle = None
gun_follow = False

CHEAT_FIRE_COOLDOWN = 6
cheat_cooldown = 0
AIM_TOLERANCE_DEG = 3

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
enemy_speed = 2

player_health = 5
player_key=0
score = 0
player_dead = False
missed_bullets = 0
BULLET_SPEED = 15
BULLET_SIZE = 7
BULLET_LIFE = 60
bullets = []



def draw_chest(x, y, z=0, length=70, width=50, height=40, top_height=20):
    """Draws a chest at position (x, y, z) with cuboid base and half-cylinder top."""
    
    # --- Cuboid base (chest body) ---
    glColor3f(0.545, 0.271, 0.075)  # Brown color for the chest base (wood-like)
    
    glPushMatrix()
    glTranslatef(x, y, z)  # Position the chest
    
    # Draw the chest body (cuboid)
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
    
    # --- Half-cylinder top ---
    glColor3f(0.8, 0.4, 0.2)  # Lighter wood-like color for the top
    
    # Draw the half-cylinder top (rounded part of the chest)
    glPushMatrix()
    glTranslatef(x, y, z + height)  # Position the half-cylinder on top of the cuboid
    glRotatef(90, 1, 0, 0)  # Rotate to get the half-cylinder's curved part facing upward
    gluCylinder(gluNewQuadric(), length / 2, length / 2, top_height, 20, 20)  # Create the half-cylinder top
    glPopMatrix()

    glPopMatrix()




def spawn_enemies():
    global enemies
    enemies = []
    for i in range(5):
        x = random.randint(-GRID_LENGTH - 1000, GRID_LENGTH + 1000)
        y = random.randint(-GRID_LENGTH - 1000, GRID_LENGTH + 1000)
        enemies.append((x, y))
    x = -1465.2414404826753
    y = 774.4560684762663
    for drones in range(10):

        x = random.randint(-1500, -600)
        y = random.randint( 600, 1200)
        enemies.append((x, y))


def move_enemies_towards_player():
    room_x_min, room_x_max = -1500, -600  # Room x boundaries
    room_y_min, room_y_max = 400, 1300
    global player_health, player_dead
    if player_health == 0:
        return
    COLLISION_DIST = 35
    for i in range(len(enemies)):
        ex, ey = enemies[i]
        px, py = player_pos
        dx, dy = px - ex, py - ey
        dist = math.hypot(dx, dy)
        if dist == 0:
            continue
        step_x = enemy_speed * dx / dist
        step_y = enemy_speed * dy / dist
        ex += step_x
        ey += step_y
        if dist < COLLISION_DIST and not player_dead:
            player_health -= 1
            if player_health <= 0:
                player_health = 0
                player_dead = True
            print("Player hit! Health:", player_health)
            ex = max(room_x_min + 50, min(room_x_max - 50, ex))  # Bound x within room
            ey = max(room_y_min + 50, min(room_y_max - 50, ey))
            if player_health <= 0:
                player_health = 0
        half_margin = 10
        #ex = max(-GRID_LENGTH + WALL_THICK + half_margin)
                # min(GRID_LENGTH - WALL_THICK - half_margin, ex))
       # ey = max(-GRID_LENGTH + WALL_THICK + half_margin,
                # min(GRID_LENGTH - WALL_THICK - half_margin, ey))
        enemies[i] = (ex, ey)

def draw_enemy_2(x, y, body_radius=50, head_radius=20):
    global scaling_factor
    glPushMatrix()
    glTranslatef(x, y, body_radius)

    glScalef(scaling_factor,
             scaling_factor,
             scaling_factor)
    glColor3f(1, 0, 0)
    glutSolidSphere(body_radius, 20, 20)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(x, y, body_radius + head_radius)
    glColor3f(0, 0, 0)
    glutSolidSphere(head_radius, 20, 20)
    glPopMatrix()




   


def spawn_player_bullet():
    rad = math.radians(player_angle + 90)
    spawn_x = player_pos[0] + 20 * math.cos(rad)
    spawn_y = player_pos[1] + 20 * math.sin(rad)
    bullets.append([spawn_x, spawn_y, player_angle, BULLET_LIFE])
    print("Player Bullet Fired!")

def cheat():
    global enemy_scale_factor, enemy_scale_direction, player_angle
    global cheat_cooldown
    player_angle = (player_angle + SPIN_SPEED_DEG) % 360
    if cheat_cooldown > 0:
        cheat_cooldown -= 1
    if cheat_cooldown == 0:
        px, py = player_pos
        for ex, ey in enemies:
            angle_to_enemy = (math.degrees(math.atan2(ey - py, ex - px)) - 90) % 360
            diff = min((angle_to_enemy - player_angle) % 360,
                       (player_angle - angle_to_enemy) % 360)
            if diff < AIM_TOLERANCE_DEG:
                spawn_player_bullet()
                cheat_cooldown = CHEAT_FIRE_COOLDOWN
                break

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
    global enemy_scale_factor, enemy_scale_direction, player_angle
    global cheat_cooldown
    if player_dead:
        glutPostRedisplay()
        return

    if cheat_mode:
        cheat()

    shrink_expand()
    move_enemies_towards_player()
    update_bullets()
    glutPostRedisplay()


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
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


def third_person_camera():
    rad = math.radians(cam_angle)
    eye_x = cam_radius * math.cos(rad)
    eye_y = cam_radius * math.sin(rad)
    eye_z = cam_radius * math.sin(math.radians(cam_elev))
    gluLookAt(eye_x, eye_y, eye_z,
              0, 0, 0,
              0, 0, 1)

def first_person_camera():
    global player_pos, player_angle, cheat_mode, cheat_cam_angle, gun_follow
    if cheat_mode == True:
        if gun_follow == True:
            view_angle = player_angle
        else:
            view_angle = cheat_cam_angle
    else:
        view_angle = player_angle

    dir_rad = math.radians(view_angle + 90)
    dir_x = math.cos(dir_rad)
    dir_y = math.sin(dir_rad)
    eye_x = player_pos[0] - BACK_OFFSET * dir_x
    eye_y = player_pos[1] - BACK_OFFSET * dir_y
    eye_z = HEAD_HEIGHT
    look_x = player_pos[0] + LOOK_DISTANCE * dir_x
    look_y = player_pos[1] + LOOK_DISTANCE * dir_y
    look_z = HEAD_HEIGHT
    gluLookAt(eye_x, eye_y, eye_z,
              look_x, look_y, look_z,
              0, 0, 1)

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if cam_mode == "tp":
        third_person_camera()
    else:
        first_person_camera()


def update_bullets():
    global bullets, enemies, score, missed_bullets, player_health, player_dead,orange_screen_flag,crates
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
        #if abs(x) > GRID_LENGTH or abs(y) > GRID_LENGTH or life <= 0:
         #   missed_bullets = missed_bullets + 1
           # print("Player missed bullets:", missed_bullets)
           # if missed_bullets >= 10 and not player_dead:
           #     player_health = 0
           #     player_dead = True
       #     continue
        hit_enemy = False
        j = 0
        while j < len(enemies):
            enemy_pos = enemies[j]
            ex = enemy_pos[0]
            ey = enemy_pos[1]
            if math.hypot(x - ex, y - ey) < 28:
                score = score + 1
                rx = random.randint(-GRID_LENGTH + 50, GRID_LENGTH - 50)
                ry = random.randint(-GRID_LENGTH + 50, GRID_LENGTH - 50)
                enemies[j] = (rx, ry)
                hit_enemy = True
                break
            j = j + 1

        if not hit_enemy:
            keep_list.append([x, y, ang, life])
    
        i=0
        while i < len(explosive_drums):
            drum_pos = explosive_drums[i]
            drum_x = drum_pos[0]
            drum_y = drum_pos[1]
            if math.hypot(x - drum_x, y - drum_y) < 50:
                dx = 5000
                dy = 5000
                explosive_drums[i]=(dx,dy)
                hit_enemy = True
                print("drum hit!")
                for e in range(len(enemies)):
                    ex = random.randint(-GRID_LENGTH - 1000, GRID_LENGTH + 1000)
                    ey = random.randint(-GRID_LENGTH - 1000, GRID_LENGTH + 1000)
                    enemies[e]=(ex,ey)
                    score+=1
                orange_screen_flag=True
                break
            i+=1 
        p=0
        while p < len(crates):
            crate_pos = crates[p]
            crate_x = crate_pos[0]
            crate_y = crate_pos[1]
            if math.hypot(x - crate_x, y - crate_y) < 35:
                cx = 1500
                cy = 1500
                crates[p]=(cx,cy)
                hit_enemy = True
                print("crate hit!",crates[p])
                
                
            p = p + 1
    bullets = keep_list
   
def draw_sphere(x, y, z, radius,color):
    """
    Draws a green sphere at the given position (x, y, z) with a specified radius.

    :param x: X-coordinate for the center of the sphere
    :param y: Y-coordinate for the center of the sphere
    :param z: Z-coordinate for the center of the sphere
    :param radius: Radius of the sphere
    """
    if color=="green":
        glPushMatrix()
        glTranslatef(x, y, z)  # Position the sphere at (x, y, z)
    
        glColor3f(0.0, 1.0, 0.0)  # Set the color to green

    # Draw the sphere using gluSphere (with the specified radius)
        gluSphere(gluNewQuadric(), radius, 20, 20)

        glPopMatrix()

    elif color=="gold":
        glPushMatrix()
        glTranslatef(x, y, z)  # Position the sphere at (x, y, z)
    
        glColor3f(1.0, 0.84, 0.0)  # Set the color to green

    # Draw the sphere using gluSphere (with the specified radius)
        gluSphere(gluNewQuadric(), radius, 20, 20)

        glPopMatrix()



def draw_room(x, y, width, depth, height, door_width=100, door_height=150):
    """Draws a large open-top room (4 walls, no ceiling or floor) with an open door on the front wall, and a floor."""
    glColor3f(0.5, 0.5, 0.5)  # Wall color (light brown)

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
    glColor3f(199/255,157/255,122/255)

    glPushMatrix()
    glTranslatef(x, y, z)  # Position the crate

    # Draw the crate (simple cube)
    glBegin(GL_QUADS)
    
    # Front face
    glVertex3f(-crate_size/2, -crate_size/2, crate_size/2)
    glVertex3f(crate_size/2, -crate_size/2, crate_size/2)
    glVertex3f(crate_size/2, crate_size/2, crate_size/2)
    glVertex3f(-crate_size/2, crate_size/2, crate_size/2)

    # Back face
    glVertex3f(-crate_size/2, -crate_size/2, -crate_size/2)
    glVertex3f(crate_size/2, -crate_size/2, -crate_size/2)
    glVertex3f(crate_size/2, crate_size/2, -crate_size/2)
    glVertex3f(-crate_size/2, crate_size/2, -crate_size/2)

    # Left face
    glVertex3f(-crate_size/2, -crate_size/2, crate_size/2)
    glVertex3f(-crate_size/2, -crate_size/2, -crate_size/2)
    glVertex3f(-crate_size/2, crate_size/2, -crate_size/2)
    glVertex3f(-crate_size/2, crate_size/2, crate_size/2)

    # Right face
    glVertex3f(crate_size/2, -crate_size/2, crate_size/2)
    glVertex3f(crate_size/2, -crate_size/2, -crate_size/2)
    glVertex3f(crate_size/2, crate_size/2, -crate_size/2)
    glVertex3f(crate_size/2, crate_size/2, crate_size/2)

    # Top face
    glVertex3f(-crate_size/2, crate_size/2, crate_size/2)
    glVertex3f(crate_size/2, crate_size/2, crate_size/2)
    glVertex3f(crate_size/2, crate_size/2, -crate_size/2)
    glVertex3f(-crate_size/2, crate_size/2, -crate_size/2)

    # Bottom face
    glVertex3f(-crate_size/2, -crate_size/2, crate_size/2)
    glVertex3f(crate_size/2, -crate_size/2, crate_size/2)
    glVertex3f(crate_size/2, -crate_size/2, -crate_size/2)
    glVertex3f(-crate_size/2, -crate_size/2, -crate_size/2)

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
    glVertex3f(-800 + 100, 400,50)  # Bottom-right (door)
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
    horizontal_mud_y = 0       # Y position of horizontal path (middle)
    vertical_mud_x = 100       # X position of vertical path

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


def draw_enemy():
    glPushMatrix()
    glTranslatef(0, 0, 30)
    glScalef(enemy_scale_factor,
             enemy_scale_factor,
             enemy_scale_factor)
    glColor3f(1, 0, 0)
    gluSphere(gluNewQuadric(), 30, 15, 15)
    glColor3f(0, 0, 0)
    glPushMatrix()
    glTranslatef(0, 0, 30)
    gluSphere(gluNewQuadric(), 15, 10, 10)
    glPopMatrix()
    glPopMatrix()

def draw_tree(x, y, z=0):
    """Draws a simple tree at position (x, y, z)."""
    
    trunk_height = 200  # Height of the tree trunk
    trunk_radius = 10   # Radius of the trunk
    crown_radius = 50   # Radius of the tree crown (leaves)
    
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
        glColor3f(0, 0, 1)
        glRotatef(-90, 1, 0, 0)
        glTranslatef(0, -40, 0)
    else:
        glColor3f(0, 0, 1)
    glPushMatrix()
    glTranslatef(-20, 0, 0)
    gluCylinder(gluNewQuadric(), 4, 7, 40, 10, 10)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(20, 0, 0)
    gluCylinder(gluNewQuadric(), 4, 7, 40, 10, 10)
    glPopMatrix()
    glTranslatef(0, 0, 40)
    glColor3f(0, 0.6, 0)
    glPushMatrix()
    glScalef(2, 1.2, 2)
    glutSolidCube(20)
    glPopMatrix()
    glColor3f(0.8, 0.8, 0.8)
    glPushMatrix()
    glTranslatef(0, 12, 15)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 8, 4, 45, 10, 10)
    glPopMatrix()
    glColor3f(1, 0.8, 0.6)
    glPushMatrix()
    glTranslatef(-16, 10, 10)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 6, 4, 25, 10, 10)
    glPopMatrix()
    glColor3f(1, 0.8, 0.6)
    glPushMatrix()
    glTranslatef(16, 10, 10)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 6, 4, 25, 10, 10)
    glPopMatrix()
    glColor3f(0, 0, 0)
    glPushMatrix()
    glTranslatef(0, 0, 37)
    gluSphere(gluNewQuadric(), 12, 10, 10)
    glPopMatrix()
    glPopMatrix()





def if_dead():
    global cheat_cooldown, cam_mode, player_pos, player_angle, player_health, player_dead
    global missed_bullets, score, cheat_mode, cheat_cam_angle, gun_follow
    cam_mode = "tp"
    cheat_cam_angle = None
    gun_follow = False
    cheat_mode = False
    player_dead = False
    player_pos[:] = [0, 0]
    player_health = 7
    missed_bullets = 0
    score = 0
    bullets.clear()
    cheat_cooldown = 0
    spawn_enemies()
    return

def cheat_on():
    global cheat_cooldown, cam_mode, player_pos, player_angle, player_health, player_dead
    global missed_bullets, score, cheat_mode, cheat_cam_angle, gun_follow
    cheat_mode = not cheat_mode
    if cheat_mode and cam_mode == "fp":
        cheat_cam_angle = player_angle
    else:
        cheat_cam_angle = None
    return

def keyboardListener(key, x, y):
    global cheat_cooldown, cam_mode, player_pos, player_angle, player_health, player_dead,orange_screen_flag
    global missed_bullets, score, cheat_mode, cheat_cam_angle, gun_follow
    move_speed = 20
    if player_dead:
        if key in (b'r', b'R'):
            if_dead()
            return
        else:
            return
    
    if key in (b'q', b'q') and orange_screen_flag:
        orange_screen_flag =False

    if key in (b'c', b'C') and not player_dead:
        cheat_on()

    if key in (b'v', b'V') and cheat_mode and cam_mode == "fp":
        gun_follow = not gun_follow
        if gun_follow:
            cheat_cam_angle = None
        else:
            cheat_cam_angle = player_angle
        return


    if key == b'a':
        player_angle = (player_angle + 5) % 360
    elif key == b'd':
        player_angle = (player_angle - 5) % 360
    rad = math.radians(player_angle + 90)
    dx = math.cos(rad) * move_speed
    dy = math.sin(rad) * move_speed

    if key == b'w':
            player_pos[0] += dx
            player_pos[1] += dy
            orange_screen_flag =False

    elif key == b's':
        player_pos[0] -= dx
        print(player_pos[0])
        print(player_pos[1])
        player_pos[1] -= dy
        orange_screen_flag =False


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
    global cam_mode, cheat_mode, cheat_cam_angle, gun_follow
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN and not player_dead:
        spawn_player_bullet()
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        if cam_mode == "tp":
            cam_mode = "fp"
            if cheat_mode and not gun_follow:
                cheat_cam_angle = player_angle
        else:
            cam_mode = "tp"
            cheat_cam_angle = None
            gun_follow = False
        glutPostRedisplay()

def showScreen():
    global score, player_health,explosive_drums,orange_screen_flag,health_packs
    rotation_angle=0
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    setupCamera()
    draw_bullets()
    # Draw an enemy at position (50, 100, 0) with body size 4, head size 1.5, and limb size 1
    
        # Rotate the pill slowly in a clockwise direction around the y-axis
    glPushMatrix()
    glRotatef(rotation_angle, 0.0, 1.0, 0.0)  # Rotate around the y-axis
    
    glPopMatrix()

    # Update the rotation angle for the next frame (slow clockwise rotation)
    rotation_angle += 0.1  # Slow rotation speed
    if rotation_angle > 360:
        rotation_angle -= 360 
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], 1)
    glRotatef(player_angle, 0, 0, 1)
    draw_player()

    glPopMatrix()
    #draw_enemy_2(0,0,50,25)
  
    draw_walls()
    for x in explosive_drums:
        drum_pos_x=x[0]
        drum_pos_y=x[1]
        drum_pos_z=0
        draw_explosive_drum(drum_pos_x, drum_pos_y, drum_pos_z)
    
    for c in crates:
        c_pos_x=c[0]
        c_pos_y=c[1]
        c_pos_z=50
        draw_crate(c_pos_x, c_pos_y, c_pos_z)
    
    
    for g in range(len(health_packs)-1):
        
        
        if abs(player_pos[0]-health_packs[g][0])<15 and abs(player_pos[1]-health_packs[g][1])<15:
            player_health+=2
            del health_packs[g]

        else:
            draw_sphere (health_packs[g][0], health_packs[g][1], 70,15,"green")
    
    for key in range(len(keys)):
        
        
        if abs(player_pos[0]-keys[key][0])<15 and abs(player_pos[1]-keys[key][1])<15:
            player_key+=1
            del keys[key]

        else:
            draw_sphere (keys[key][0], keys[key][1], 70,8,"gold")




    

  
    


    

    tile_size = 50
    #draw_tree(300,250,0)
    draw_tree(300,-250,0)
    val_x=300
    val_y=-250
    c_x=-100
    c_y=-250
    g_x=-100
    g_y=300
    r_x=283.1811161232042+350
    r_y=188.05407289332277
    for i in range(10):
         draw_tree(r_x,r_y,0)
         r_x+=350
    for i in range(17):
         draw_tree(val_x,g_y,0)
         g_y+=300
    
    for i in range(10):
         draw_tree(val_x,val_y,0)
         val_y-=300
    
    for i in range(10):
        draw_tree(c_x,c_y,0)
        c_y-=300

    if orange_screen_flag:
        glColor3f(1.0, 0.647, 0.0)  # Orange color
        glBegin(GL_QUADS)  # Start drawing a quad
        glVertex2f(-1000, -1000)  # Bottom-left corner (normalized coordinates)
        glVertex2f(1000, -1000)   # Bottom-right corner
        glVertex2f(1000, 1000)    # Top-right corner
        glVertex2f(-1000, 1000)   # Top-left corner
        glEnd()  # End drawing the quad


    
    



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
        glPushMatrix()
        glTranslatef(enemy_pos[0], enemy_pos[1], 0)
        draw_enemy()
        glPopMatrix()
    draw_text(10, 770, f"Player Life Remaining: {player_health}")
    if player_dead:
        draw_text(10, 740, "GAME OVER!!! press R to restart")
        draw_text(10, 710, " ")
    else:
        draw_text(10, 740, f"Game Score: {score}")
        draw_text(10, 710, f"Player Bullet Missed: {missed_bullets}")
    glutSwapBuffers()

def main():
    glutInit()
    generate_terrain()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(300, 100)
    glutCreateWindow(b"Boom!!!!")
    glEnable(GL_DEPTH_TEST)
    spawn_enemies()
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(animate)
    glutMainLoop()


if __name__ == "__main__":
    main()