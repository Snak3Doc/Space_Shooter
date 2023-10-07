# main.py
### Imports ###
import pathlib
import sys
from random import choice, randint
from time import sleep

import pygame as pg
pg.init()
from rich import print
from rich.traceback import install
install(show_locals=True)

### Data ###
game_over = False
delta_time = 0

SCREEN_WIDTH = 720
SCREEN_HEIGHT = 720

SPRITE_WIDTH = 40
SPRITE_HEIGHT = 40

FPS = 60

POWER_RATE = 15
power_timer = POWER_RATE

WORK_DIR = pathlib.Path.cwd()

LARGE_FONT = pg.font.Font(WORK_DIR/"game_assets"/"game_font.ttf", 30)
SMALL_FONT = pg.font.Font(WORK_DIR/"game_assets"/"game_font.ttf", 16)

#* Paths
BG_IMG_PATH = WORK_DIR/"game_assets"/"UI"/"space_background.png"
BG_IMG = pg.transform.scale(pg.image.load(BG_IMG_PATH), (SCREEN_WIDTH, SCREEN_HEIGHT))

PLAYER_IMG_PATH = WORK_DIR/"game_assets"/"Players"/"playerShip1_green.png"

LASER_IMG_PATH = WORK_DIR/"game_assets"/"Lasers"/"laserGreen11.png"

ENEMY_IMG_PATH_1 = WORK_DIR/"game_assets"/"Enemies"/"enemyRed1.png"
ENEMY_IMG_PATH_2 = WORK_DIR/"game_assets"/"Enemies"/"enemyRed2.png"
ENEMY_IMG_PATH_3 = WORK_DIR/"game_assets"/"Enemies"/"enemyRed3.png"
ENEMY_IMG_PATH_4 = WORK_DIR/"game_assets"/"Enemies"/"enemyRed4.png"
ENEMY_IMG_PATH_5 = WORK_DIR/"game_assets"/"Enemies"/"enemyRed5.png"

METEOR_IMG_PATH_1 = WORK_DIR/"game_assets"/"Meteors"/"meteorBrown_med1.png"
METEOR_IMG_PATH_2 = WORK_DIR/"game_assets"/"Meteors"/"meteorBrown_med3.png"
METEOR_IMG_PATH_3 = WORK_DIR/"game_assets"/"Meteors"/"meteorBrown_small1.png"
METEOR_IMG_PATH_4 = WORK_DIR/"game_assets"/"Meteors"/"meteorBrown_small2.png"
METEOR_IMG_PATH_5 = WORK_DIR/"game_assets"/"Meteors"/"meteorBrown_tiny1.png"
METEOR_IMG_PATH_6 = WORK_DIR/"game_assets"/"Meteors"/"meteorBrown_tiny2.png"

HP_IMG_PATH = WORK_DIR/"game_assets"/"Power-ups"/"pill_red.png"
FR_IMG_PATH = WORK_DIR/"game_assets"/"Power-ups"/"bolt_gold.png"

LASER_SFX_PATH = WORK_DIR/"game_assets"/"Audio"/"laserSmall_002.ogg"
EXPLOSION_SFX_PATH = WORK_DIR/"game_assets"/"Audio"/"explosionCrunch_000.ogg"

#* Path Lists
ENEMY_IMG_PATHS = [ENEMY_IMG_PATH_1, ENEMY_IMG_PATH_2, ENEMY_IMG_PATH_3,
                   ENEMY_IMG_PATH_4, ENEMY_IMG_PATH_5]

METEOR_IMG_PATHS = [METEOR_IMG_PATH_1, METEOR_IMG_PATH_2, METEOR_IMG_PATH_3,
                    METEOR_IMG_PATH_4, METEOR_IMG_PATH_5, METEOR_IMG_PATH_6]


### Window Setup ###
mw = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption("Space Shooter")
clock = pg.time.Clock()

### Classes ###
class BaseSprite(pg.sprite.Sprite):
    def __init__(self, img_path, scale_width, scale_height, x_pos, y_pos, step):
        super().__init__()
        if scale_width is not None and scale_height is not None:
            self.image = pg.transform.scale(pg.image.load(img_path), (scale_width, scale_height))
        else:
            self.image = pg.image.load(img_path)

        self.rect = self.image.get_rect()
        self.rect.x = x_pos
        self.rect.y = y_pos

        self.step = step
        self.width = self.image.get_width()
        self.height = self.image.get_height()

class PlayerSprite(BaseSprite):
    def __init__(self, img_path, scale_width, scale_height, x_pos, y_pos, step):
        super().__init__(img_path, scale_width, scale_height, x_pos, y_pos, step)
        self.start_x = x_pos
        self.start_y = y_pos

        self.lives = 3
        self.score = 0

        self.FIRE_RATE = 0.5
        self.shot_timer = self.FIRE_RATE
        self.fr_power_timer = None # Initialize the timer

    def update(self):
        pressed_keys = pg.key.get_pressed()

        if pressed_keys[pg.K_a] and self.rect.x >=0:
            self.rect.x -= self.step

        if pressed_keys[pg.K_d] and self.rect.x <= SCREEN_WIDTH - SPRITE_WIDTH:
            self.rect.x += self.step

        self.shot_timer -= delta_time
        if pressed_keys[pg.K_SPACE] and self.shot_timer <= 0:
            laser_sfx.play()
            self.shot_timer = self.FIRE_RATE
            laser = LaserSprite(LASER_IMG_PATH, 6, 36, self.rect.centerx - 3, self.rect.y - 20, 4)
            laser_sprite_group.add(laser)

        if self.FIRE_RATE != 0.5:
            if self.fr_power_timer is None:
                self.fr_power_timer = pg.time.get_ticks()
            elif pg.time.get_ticks() - self.fr_power_timer >= 5000: # 5000 == 5s
                self.FIRE_RATE = 0.5
                self.fr_power_timer = None

class LaserSprite(BaseSprite):
    def update(self):
        if self.rect.y > -self.rect.height:
            self.rect.y -= self.step
            if pg.sprite.groupcollide(laser_sprite_group, enemy_sprite_group, True, True):
                explosion_sfx.play()
                del self
                player.score += 10

        else:
            print("Laser deleted")
            laser_sprite_group.remove(self)
            del self

class EnemySprite(BaseSprite):
    def update(self):
        if self.rect.y <= SCREEN_HEIGHT:
            self.rect.y += self.step
            if pg.sprite.spritecollide(player, enemy_sprite_group, True):
                del self
                player.lives -= 1

        else:
            print("Enemy deleted")
            enemy_sprite_group.remove(self)
            del self
            player.lives -= 1

class MeteorSprite(BaseSprite):
    def update(self):
        if self.rect.y <= SCREEN_HEIGHT:
            self.rect.y += self.step
            if pg.sprite.groupcollide(player_sprite_group, meteor_sprite_group, True, True):
                explosion_sfx.play()
                del self
                player.lives = 0
                print("Player hit by Meteor")

            if pg.sprite.groupcollide(enemy_sprite_group, meteor_sprite_group, True, False):
                explosion_sfx.play()
                print("Enemy hit by Meteor")
                pass

        else:
            print("Meteor deleted")
            meteor_sprite_group.remove(self)
            del self

class HPPowerSprite(BaseSprite):
    def update(self):
        if self.rect.y <= SCREEN_HEIGHT:
            self.rect.y += self.step
            if pg.sprite.spritecollide(player, power_up_sprite_group, True):
                print("Power up added to player")
                del self
                player.lives = 3

        else:
            print("Power up deleted")
            power_up_sprite_group.remove(self)
            del self

class FRPowerSprite(BaseSprite):
    def update(self):
        if self.rect.y <= SCREEN_HEIGHT:
            self.rect.y += self.step
            if pg.sprite.spritecollide(player, power_up_sprite_group, True):
                print("Power up added to player")
                del self
                player.FIRE_RATE = 0.2

        else:
            print("Power up deleted")
            power_up_sprite_group.remove(self)
            del self


### Functions ###
def check_exit(event):
    if event.type == pg.QUIT:
        pg.quit()
        sys.exit()

def spawn_enemies():
    if len(enemy_sprite_group) < 5:
        enemy = EnemySprite(choice(ENEMY_IMG_PATHS),
                            SPRITE_WIDTH, SPRITE_HEIGHT,
                            randint(SPRITE_WIDTH, SCREEN_WIDTH - SPRITE_WIDTH * 2),
                            -(randint(SPRITE_HEIGHT, SPRITE_HEIGHT * 6)),
                            randint(1, 2))
        enemy_sprite_group.add(enemy)

def spawn_meteors():
    if len(meteor_sprite_group) < 2:
        meteor = MeteorSprite(choice(METEOR_IMG_PATHS),
                            None, None,
                            randint(SPRITE_WIDTH, SCREEN_WIDTH - SPRITE_WIDTH * 2),
                            -(randint(SPRITE_HEIGHT, SPRITE_HEIGHT * 6)),
                            randint(2, 4))
        meteor_sprite_group.add(meteor)

def spawn_power(POWER_RATE, power_timer, delta_time):
    power_timer -= delta_time
    #!print(f"Power Timer: {power_timer}")
    if power_timer <= 0:
        power_timer = POWER_RATE
        spawn = bool(randint(0, 1))
        print(f"Spawn = {spawn}")
        if spawn:
            power_type = randint(0, 1)
            if power_type == 0:
                power_up = HPPowerSprite(HP_IMG_PATH,
                                    None, None,
                                    randint(SPRITE_WIDTH, SCREEN_WIDTH - SPRITE_WIDTH * 2),
                                    -(randint(SPRITE_HEIGHT, SPRITE_HEIGHT * 6)),
                                    randint(2, 4))
                power_up_sprite_group.add(power_up)
            elif power_type == 1:
                power_up = FRPowerSprite(FR_IMG_PATH,
                                    None, None,
                                    randint(SPRITE_WIDTH, SCREEN_WIDTH - SPRITE_WIDTH * 2),
                                    -(randint(SPRITE_HEIGHT, SPRITE_HEIGHT * 6)),
                                    randint(2, 4))
                power_up_sprite_group.add(power_up)

    return power_timer


def check_game_over():
    if player.lives <= 0:
        text_image_1 = LARGE_FONT.render(f"Game Over!", True, (214, 214, 214))
        text_image_2 = LARGE_FONT.render(f"Total Score", True, (214, 214, 214))
        text_image_3 = LARGE_FONT.render(f"{player.score}", True, (214, 214, 214))

        text_rect_1 = text_image_1.get_rect()
        text_rect_2 = text_image_2.get_rect()
        text_rect_3 = text_image_3.get_rect()

        text_rect_1.center = (SCREEN_WIDTH/2, 340)
        text_rect_2.center = (SCREEN_WIDTH/2, 390)
        text_rect_3.center = (SCREEN_WIDTH/2, 440)


        mw.blit(text_image_1, text_rect_1)
        mw.blit(text_image_2, text_rect_2)
        mw.blit(text_image_3, text_rect_3)

        pg.display.update()
        sleep(2)
        pg.quit()
        sys.exit()

def draw_score():
    text_image = SMALL_FONT.render(f"Score {player.score}", True, (214, 214, 214))
    mw.blit(text_image, (15, 10))

def draw_lives():
    text_image = SMALL_FONT.render(f"{player.lives} Lives", True, (214, 214, 214))
    mw.blit(text_image, (600, 10))


### Objects and Groups ###
#* Groups
player_sprite_group = pg.sprite.Group()
laser_sprite_group = pg.sprite.Group()
enemy_sprite_group = pg.sprite.Group()
meteor_sprite_group = pg.sprite.Group()
power_up_sprite_group = pg.sprite.Group()

#* Sprites
player = PlayerSprite(PLAYER_IMG_PATH, SPRITE_WIDTH, SPRITE_HEIGHT, 360, 650, 5)

#*Adding Sprites to groups
player_sprite_group.add(player)

#* Audio
laser_sfx = pg.mixer.Sound(LASER_SFX_PATH)
explosion_sfx = pg.mixer.Sound(EXPLOSION_SFX_PATH)


### Game Loop ###
while not game_over:
    mw.blit(BG_IMG, (0, 0))

    check_game_over()
    draw_lives()
    draw_score()

    spawn_enemies()
    spawn_meteors()
    power_timer = spawn_power(POWER_RATE, power_timer, delta_time)

    laser_sprite_group.update()
    player_sprite_group.update()
    enemy_sprite_group.update()
    meteor_sprite_group.update()
    power_up_sprite_group.update()
    

    laser_sprite_group.draw(mw)
    player_sprite_group.draw(mw)
    enemy_sprite_group.draw(mw)
    meteor_sprite_group.draw(mw)
    power_up_sprite_group.draw(mw)


    for event in pg.event.get():
        check_exit(event)

    pg.display.update()
    delta_time = clock.tick(FPS) / 1000