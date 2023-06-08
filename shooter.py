#boilerplate.py

### Imports ###
import pygame
pygame.init()
import pathlib
import sys
import random
from time import sleep

# Dev tools
from rich import print # Pretty Prints
from rich.traceback import install # Pretty Tracebacks
install(show_locals=True)

### Constants ###
SCREEN_WIDTH = 720
SCREEN_HEIGHT = 720
SPRITE_WIDTH = 40
SPRITE_HEIGHT = 40

FPS = 60
FIRE_RATE = 0.5


WORK_DIR = pathlib.Path.cwd()

# File Paths
BG_IMG_PATH = WORK_DIR/"game_assets"/"UI"/"space_background.png"

PLAYER_IMG_PATH = WORK_DIR/"game_assets"/"Players"/"playerShip1_orange.png"

ENEMY_IMG_PATH_1 = WORK_DIR/"game_assets"/"Enemies"/"enemyBlue1.png"
ENEMY_IMG_PATH_2 = WORK_DIR/"game_assets"/"Enemies"/"enemyBlue2.png"
ENEMY_IMG_PATH_3 = WORK_DIR/"game_assets"/"Enemies"/"enemyBlue3.png"
ENEMY_IMG_PATH_4 = WORK_DIR/"game_assets"/"Enemies"/"enemyBlue4.png"
ENEMY_IMG_PATH_5 = WORK_DIR/"game_assets"/"Enemies"/"enemyBlue5.png"

LASER_IMG_PATH = WORK_DIR/"game_assets"/"Lasers"/"laserGreen07.png"

METEOR_IMG_PATH_1 = WORK_DIR/"game_assets"/"Meteors"/"meteorBrown_med1.png"
METEOR_IMG_PATH_2 = WORK_DIR/"game_assets"/"Meteors"/"meteorBrown_med3.png"
METEOR_IMG_PATH_3 = WORK_DIR/"game_assets"/"Meteors"/"meteorBrown_small1.png"
METEOR_IMG_PATH_4 = WORK_DIR/"game_assets"/"Meteors"/"meteorBrown_small2.png"
METEOR_IMG_PATH_5 = WORK_DIR/"game_assets"/"Meteors"/"meteorBrown_tiny1.png"
METEOR_IMG_PATH_6 = WORK_DIR/"game_assets"/"Meteors"/"meteorBrown_tiny2.png"


SHOOT_SFX_PATH = WORK_DIR/"game_assets"/"Audio"/"laserLarge_000.ogg"
EXPLODE_SFX_PATH = WORK_DIR/"game_assets"/"Audio"/"explosionCrunch_000.ogg"

# Load Images
BG_IMG = pygame.image.load(BG_IMG_PATH)


### Variables ###
game_over = False
delta_time = 0

small_font = pygame.font.Font(WORK_DIR/"game_assets"/"game_font.ttf", 16)
large_font = pygame.font.Font(WORK_DIR/"game_assets"/"game_font.ttf", 30)


### Lists ###
ENEMY_IMG_PATHS = [ENEMY_IMG_PATH_1, ENEMY_IMG_PATH_2, ENEMY_IMG_PATH_3, ENEMY_IMG_PATH_4, ENEMY_IMG_PATH_5]
METEOR_IMG_PATHS = [METEOR_IMG_PATH_1, METEOR_IMG_PATH_2,
                    METEOR_IMG_PATH_3, METEOR_IMG_PATH_4, METEOR_IMG_PATH_5,
                    METEOR_IMG_PATH_6]


### Window Setup ###
main_win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()

### Classes ###
class SpriteBase(pygame.sprite.Sprite):
    def __init__(self, img_path, x_pos, y_pos, scale_width, scale_height, step):
        super().__init__()
        if scale_width is not None and scale_height is not None:
            self.image = pygame.transform.scale(pygame.image.load(img_path), (scale_width, scale_height))
        else:
            self.image = pygame.image.load(img_path)

        self.rect = self.image.get_rect()
        self.rect.x = x_pos
        self.rect.y = y_pos

        self.step = step

        self.width = self.image.get_width()
        self.height = self.image.get_height()

        self.top_limit = 5
        self.bottom_limit = SCREEN_HEIGHT - self.height - 5
        self.left_limit = 5
        self.right_limit = SCREEN_WIDTH -  self.width - 5

class PlayerSprite(SpriteBase):
    def __init__(self, img_path, x_pos, y_pos, scale_width, scale_height, step): 
        super().__init__(img_path, x_pos, y_pos, scale_width, scale_height, step)
        self.start_x = x_pos
        self.start_y = y_pos
        self.shot_timer = FIRE_RATE
        self.score = 0
        self.lives = 3


    def update(self):
        pressed_keys = pygame.key.get_pressed()

        #* Check if the a or d key is in pressed_keys
        if pressed_keys[pygame.K_a] and self.rect.x > self.left_limit:
            self.rect.x -= self.step

        if pressed_keys[pygame.K_d] and self.rect.x < self.right_limit:
            self.rect.x += self.step

        self.shot_timer -= delta_time
        if pressed_keys[pygame.K_SPACE] and self.shot_timer <= 0:
            SHOOT_SFX.play()
            self.shot_timer = FIRE_RATE
            laser = LaserSprite(LASER_IMG_PATH, self.rect.centerx - 2, self.rect.y - 30, 4, 28, 4)
            laser_sprite_group.add(laser)


class LaserSprite(SpriteBase):
    def update(self):
        if self.rect.y > -57:
            self.rect.y -= self.step
            if pygame.sprite.groupcollide(laser_sprite_group, enemy_sprite_group, True, True):
                EXPLODE_SFX.play()
                del self
                player.score += 10
            if pygame.sprite.groupcollide(laser_sprite_group, meteor_sprite_group, True, False):
                del self
        else:
            laser_sprite_group.remove(self)
            del self


class EnemySprite(SpriteBase):
    def update(self):
        if self.rect.y < SCREEN_HEIGHT:
            self.rect.y += self.step
            if pygame.sprite.spritecollide(player, enemy_sprite_group, True):
                del self
                player.lives -= 1
        else:
            enemy_sprite_group.remove(self)
            del self
            player.lives -= 1

class MeteorSprite(SpriteBase):
    def update(self):
        if self.rect.y < SCREEN_HEIGHT:
            self.rect.y += self.step
            if pygame.sprite.groupcollide(player_sprite_group, meteor_sprite_group, True, True):
                player.lives = 0
            if pygame.sprite.groupcollide(enemy_sprite_group, meteor_sprite_group, True, False):
                print("Meteor hit enemy")
                pass
        else:
            meteor_sprite_group.remove(self)
            print("Meteor of screen")
            del self



### Functions ###
def check_exit(event):
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()

def check_game_over():
    if player.lives <= 0:
        text_image_1 = large_font.render(f"Game Over!", True, (214, 214, 214))
        text_image_2 = large_font.render(f"Total Score", True, (214, 214, 214))
        text_image_3 = large_font.render(f"{str(player.score)}", True, (214, 214, 214))

        text_rect_1 = text_image_1.get_rect()
        text_rect_2 = text_image_2.get_rect()
        text_rect_3 = text_image_3.get_rect()

        text_rect_1.center = (SCREEN_WIDTH/2, 340)
        text_rect_2.center = (SCREEN_WIDTH/2, 390)
        text_rect_3.center = (SCREEN_WIDTH/2, 440)

        main_win.blit(text_image_1, text_rect_1)
        main_win.blit(text_image_2, text_rect_2)
        main_win.blit(text_image_3, text_rect_3)

        pygame.display.update()
        sleep(2)
        pygame.quit()
        sys.exit()

def spawn_enemies():
    if len(enemy_sprite_group) < 5:
        enemy = EnemySprite(
            random.choice(ENEMY_IMG_PATHS),
            random.randint(SPRITE_WIDTH, SCREEN_WIDTH - SPRITE_WIDTH * 2), -(random.randint(SPRITE_HEIGHT, SPRITE_HEIGHT * 6)),
            SPRITE_WIDTH, SPRITE_HEIGHT,
            random.randint(1, 2))
        enemy_sprite_group.add(enemy)

def spawn_meteors():
    if len(meteor_sprite_group) < 2:
        meteor = MeteorSprite(
            random.choice(METEOR_IMG_PATHS),
            random.randint(SPRITE_WIDTH, SCREEN_WIDTH - SPRITE_WIDTH * 2),
            -(random.randint(SPRITE_HEIGHT, SPRITE_HEIGHT * 6)),
            None, None, #! Fix
            random.randint(2, 4))
        meteor_sprite_group.add(meteor)

def draw_lives():
    text_image = small_font.render(f"{str(player.lives)} Lives", True, (214, 214, 214))
    main_win.blit(text_image, (600, 10))

def draw_score():
    text_image = small_font.render(f"Score {str(player.score)}", True, (214, 214, 214))
    main_win.blit(text_image, (15, 10))


### Objects & Groups ###
# Groups
player_sprite_group = pygame.sprite.Group()
enemy_sprite_group = pygame.sprite.Group()
laser_sprite_group = pygame.sprite.Group()
meteor_sprite_group = pygame.sprite.Group()

# Sprites
player = PlayerSprite(PLAYER_IMG_PATH, 360, 670, SPRITE_WIDTH, SPRITE_HEIGHT, 5)


# Adding to groups
player_sprite_group.add(player)

### Audio ###
SHOOT_SFX = pygame.mixer.Sound(SHOOT_SFX_PATH)
EXPLODE_SFX = pygame.mixer.Sound(EXPLODE_SFX_PATH)

### Game Loop ###
while not game_over:
    main_win.blit(BG_IMG, (0, 0))

    draw_lives()
    draw_score()

    check_game_over()
    spawn_enemies()
    spawn_meteors()

    laser_sprite_group.update()
    player_sprite_group.update()
    enemy_sprite_group.update()
    meteor_sprite_group.update()


    
    laser_sprite_group.draw(main_win)
    player_sprite_group.draw(main_win)
    enemy_sprite_group.draw(main_win)
    meteor_sprite_group.draw(main_win)

    for event in pygame.event.get():
        check_exit(event)

    pygame.display.update()
    delta_time = clock.tick(FPS)/1000

