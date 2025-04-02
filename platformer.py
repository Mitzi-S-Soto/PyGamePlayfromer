"""
Based off this tutorial:
https://coderslegacy.com/python/pygame-series-improvements/

Developer: Mitzi S. Soto

Graphics Assets from: www.kenney.nl

Features/Improvments Made:
-added Title Screen Menu
    -used Pygame_Menu library
    -Title Logo
    -flashing Press Space text
-added Game Over menu
-fixed player not able to wrap screen with platform (still not perfect)
-add animations to coin, player
-add varying images for platforms
-adjust platform generation to avoid next platform being too high to reach
-change game font to custom font
-improved HUD
-added sounds
-added background music
-added saving high score

"""
import sys, random, time, shelve
import pygame
from pygame.locals import *  # noqa: F403
import pygame_menu
import pygame_menu.controls as ctrl
ctrl.KEY_APPLY = pygame.K_SPACE

pygame.init()

class G:
    '''Global variables class Variables in this class will never change'''
    vec = pygame.math.Vector2 # 2 for two dimentional
    ACC = 0.5
    FRIC = -0.12

    font = pygame.font.Font("assets/pixel_font.ttf",28)
    font_gameover = pygame.font.Font('assets/pixel_font.ttf',40)

    GREEN = (2,147,87)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)

class timers:
    FPS = 60
    FramePerSec = pygame.time.Clock()

class game_var:
    game_start = False
    score = 0
    HI_SCORE = 0
    game_over = False

class display:
    HEIGHT = int(1024/2)
    WIDTH = int(768/2)
    surface = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Space Jump")

#______CLASSES_____#
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.image.load("img/player_still.png")
        self.rect = self.surf.get_rect()
        self.pos = G.vec((10, 360))
        self.vel = G.vec(0,0)
        self.acc = G.vec(0,0)
        self.jumping = False
        self.score = 0
    def move(self):
        self.acc = G.vec(0,0.5)
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_LEFT]:  # noqa: F405
            self.acc.x = -G.ACC
        if pressed_keys[K_RIGHT]:  # noqa: F405
            self.acc.x = G.ACC
        self.acc.x += self.vel.x * G.FRIC
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc
        #Allows screen wrapping for player
        hits = pygame.sprite.spritecollide(self, platforms, False) 
        if self.pos.x > display.WIDTH:
            if not hits:
                self.pos.x = 1 
            elif hits[0].rect.left > display.WIDTH - 1:
                self.pos.x = 1
        '''for wrapping with hits may need to make it so it calculates
        where to place the sprite based on what direction the sprite was going
        in in the first place: right or left to help figure out
        how to keep player in correct spot wit -= or +='''
        if self.pos.x < 0:
            if not hits:
                self.pos.x = display.WIDTH - 1
            elif hits[0].rect.right < 1:
                self.pos.x = display.WIDTH - 1 
        self.rect.midbottom = self.pos    
    def jump(self):
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if hits and not self.jumping:
            self.surf = pygame.image.load("img/player_move.png")
            pygame.mixer.Sound('assets/jump.ogg').play()
            self.jumping = True
            self.vel.y = -15
    def cancel_jump(self):
        if self.jumping:
            if self.vel.y < -5:
                self.vel.y = -5      
    def update(self):
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if self.vel.y > 0:
            if  hits:
                if self.pos.y < hits[0].rect.bottom:               
                    self.pos.y = hits[0].rect.top +1
                    self.vel.y = 0
                    self.surf = pygame.image.load("img/player_still.png")
                    self.jumping = False              

class platform(pygame.sprite.Sprite):
    tiles = ('img/grass2.png','img/grass3.png','img/grass4.png')
    def __init__(self):
        super().__init__()
        myImage = self.tiles[random.randint(0,2)]
        self.image = pygame.image.load(myImage)
        self.surf = self.image
        self.rect = self.surf.get_rect(center = (random.randint(0,display.WIDTH-10),
                                                 random.randint(0, display.HEIGHT-30)))
        self.speed = random.randint(-1,1)
        self.moving = True
        self.hit = False
        if self.speed != 0:
            self.speed += random.randint(-1,1)
    def move(self):
        hits = self.rect.colliderect(P1.rect)
        if self.moving:  
            self.rect.move_ip(self.speed,0)
            if hits:
                P1.pos += (self.speed, 0)
            if self.speed > 0 and self.rect.left > display.WIDTH:
                self.rect.right = 0   
            if self.speed < 0 and self.rect.right < 0:
                self.rect.left = display.WIDTH              
    def generateCoin(self):
        if (self.speed == 0):
            coins.add(Coin((self.rect.centerx, self.rect.centery - 50)))

class Cloud(pygame.sprite.Sprite):
    tiles = ('img/clouda.png','img/cloudb.png','img/cloudc.png')
    def __init__(self):
        super().__init__()
        myImage = self.tiles[random.randint(0,2)]
        self.image = pygame.image.load(myImage).convert_alpha()
        self.surf = self.image
        self.rect = self.surf.get_rect()
        self.speed = random.randint(-1,1)

    def move(self): 
        self.rect.move_ip(self.speed,0)  

class Coin(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.sprite = ['img/coin_front.png','img/coin_side.png','img/coin_front.png','img/coin_side.png']
        self.sprite_counter = 0
        self.image = pygame.image.load("img/coin_front.png")
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
    def update(self):
        if self.sprite_counter < 3.5:
            self.image = pygame.image.load(self.sprite[int(self.sprite_counter)])
            self.sprite_counter += 0.05
        else:
            self.image = pygame.image.load(self.sprite[int(self.sprite_counter)])
            self.sprite_counter = 0
        if self.rect.colliderect(P1.rect):
            game_var.score += 5
            self.image = pygame.image.load('img/coin_gone.png')
            pygame.mixer.Sound('assets/coin.ogg').play()
            self.kill()


#Sprite Groups
P1 = Player()
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
coins = pygame.sprite.Group()
clouds = pygame.sprite.Group()

background = pygame.image.load('img/background.png')
gameover_bg = pygame.image.load('img/gameover_bg.png')
game_title = pygame.image.load('img/title.png')
mini_title = pygame.image.load('img/title_mini.png')

#__FUNCTIONS__#
def plat_check(platform, groupies):
    '''Checks if platforms overlap on creation'''
    if pygame.sprite.spritecollideany(platform,groupies):
        return True
    else:
        for entity in groupies:
            if entity == platform:
                continue
            if (abs(platform.rect.top - entity.rect.bottom) < 32) and (abs(platform.rect.bottom - entity.rect.top) < 32):
                return True
        C = False  # noqa: F841

def plat_gen(point = 0):
    '''Generate Platforms'''
    position_height = [0,50,75,100,125,175,200,240,275,325,400,425,475]
    while len(platforms) < 6:
        width = random.randrange(50,100)
        p = platform()
        C = True
        while C:
            p = platform()
            numa = 0
            if point > 1:
                if point < 7:
                    numa = random.randint(-1,1)
            p.rect.center = (random.randrange(0, display.WIDTH - width), -position_height[point + numa])
            C = plat_check(p, platforms)
        if point < 12:
            point += 1
        else:
            point = 0  
        p.generateCoin()
        platforms.add(p)
        all_sprites.add(p)

def cloud_gen(point = 0):
    '''Generate clouds'''
    position_height = [50,125,200,275,350,400,425,450]
    while len(clouds) < 5:
        a = Cloud()
        a.rect.center = (random.randrange(0, display.WIDTH), -position_height[point])
        if point < 7:
            point +=1
        else:
            point = 0
        clouds.add(a)
        all_sprites.add(a)

def draw_in_order():
    for entity in all_sprites:
        entity.move()
    for entity in clouds:
        display.surface.blit(entity.surf, entity.rect)
    for entity in platforms:
        display.surface.blit(entity.surf, entity.rect)
    for coin in coins:
        display.surface.blit(coin.image,coin.rect)
        coin.update()
    display.surface.blit(P1.surf, P1.rect)

def Text_Center(text_string):
    a = text_string.get_width()/2
    return a

def read_hi_score():
    shelfFile = shelve.open('score')
    if 'score' in shelfFile:
        game_var.HI_SCORE = shelfFile['score']
    else:
        shelfFile['score'] = game_var.HI_SCORE
    shelfFile.close()

def set_hi_score(score):
    if game_var.score > game_var.HI_SCORE:
        game_var.HI_SCORE = game_var.score
        shelfFile = shelve.open('score')
        shelfFile['score'] = game_var.HI_SCORE
        shelfFile.close()

def start_the_game():
    global all_sprites,platforms,coins,P1
    read_hi_score()
    all_sprites.empty()
    platforms.empty()
    coins.empty()
    P1 = Player()
    PT1 = platform()
    PT1.image = pygame.image.load('img/tile_grass.png')
    PT1.surf = pygame.transform.scale(PT1.image, (display.WIDTH, 24))
    PT1.rect = PT1.surf.get_rect(center = (display.WIDTH/2, display.HEIGHT-56))
    PT1.moving = False
    platforms.add(PT1)
    all_sprites.add(PT1, P1)
    #Create first platforms
    for x in range(6):
        C = True
        pl = platform()
        position_height = [0,125,175,225,300,350,-75]
        while C:
            pl = platform()
            pl.rect.center = (random.randrange(0, display.WIDTH - pl.rect.width), position_height[x])
            C = plat_check(pl, platforms)
        pl.generateCoin() 
        platforms.add(pl)
        all_sprites.add(pl)
    #MOVES AND reDRAWS ALL SPRITES
    for entity in all_sprites:
        display.surface.blit(entity.surf, entity.rect)
        pygame.display.update()
    #Start Game
    game_var.game_start = True
    timers.FramePerSec.tick(timers.FPS)

def restart():
    game_var.score = 0
    game_var.game_start = False
    game_var.game_over = False
    time.sleep(1)

#___MENUS then SCENES__#
#Menu using Pygame_Menu
mytheme = pygame_menu.themes.THEME_DEFAULT.copy()
mytheme.background_color=(0, 0, 0,0)
mytheme.title_background_color=(0,0,0,0)
mytheme.widget_border_width = 2
mytheme.widget_border_color = G.GREEN
mytheme.widget_font = pygame_menu.font.FONT_MUNRO
myimage = pygame_menu.baseimage.BaseImage(
    image_path='img/widget.png',
    drawing_mode=pygame_menu.baseimage.IMAGE_MODE_FILL
)
mytheme.widget_margin = (0,10)
mytheme.widget_padding = (10,15)
mytheme.widget_background_color = myimage
mytheme.widget_font_size = 24
mytheme.widget_alignment = pygame_menu.locals.ALIGN_CENTER

startmenu = pygame_menu.Menu('', 200, 400, theme=mytheme)
startmenu.column_min_width = 150
start_play = startmenu.add.button('  PLAY  ', start_the_game)
start_quit = startmenu.add.button('  QUIT  ', pygame_menu.events.EXIT)
start_play.set_max_width(100)
start_quit.set_max_width(100)

gameover = pygame_menu.Menu('', display.WIDTH, 400, theme=mytheme)
gor = gameover.add.button(' RESTART ',restart)
goq = gameover.add.button('  QUIT  ',pygame_menu.events.EXIT)
gor.set_max_width(100)
goq.set_max_width(100)

def title_scene():
    display.surface.blit(game_title,(display.WIDTH/2 - 150, 40))
    startmenu.draw(display.surface)
    startmenu.update(events)

def game_over_scene():
    display.surface.fill((255,0,0))
    display.surface.blit(gameover_bg, (0,0))
    gameover.draw(display.surface)
    gameover.update(events)
    hiscore = G.font.render('Hi SCORE: '+str(game_var.HI_SCORE), True, (255,255,255))
    score = G.font.render('Your score: '+ str(game_var.score), True, (255,255,255))
    display.surface.blit(score, (display.WIDTH/2 - Text_Center(score), display.HEIGHT/4))
    display.surface.blit(hiscore, (display.WIDTH/2 - Text_Center(score), display.HEIGHT/5))
    inputAsk = G.font_gameover.render("GAME OVER", True, G.GREEN)
    display.surface.blit(inputAsk, (display.WIDTH/2 - Text_Center(inputAsk), display.HEIGHT/3))
    pygame.display.update()

def game_hud():
    hudimage = pygame.image.load('img/hud.png')
    hudimage = pygame.transform.scale(hudimage, (display.WIDTH, 54))
    display.surface.blit(hudimage,(0,display.HEIGHT-54))
    score_text = G.font.render('Score: ' + str(game_var.score) + "     Hi Score: " + str(game_var.HI_SCORE), True, G.WHITE)
    display.surface.blit(score_text, (5,display.HEIGHT-54))
    display.surface.blit(mini_title,(display.WIDTH/2, display.HEIGHT - 30))

# Start Background Music
pygame.mixer.init()
pygame.mixer.music.load("assets/bg_music.mp3")
pygame.mixer.music.play(-1,0.0,3)
pygame.mixer.music.set_volume(0.5)

#     GAME LOOP      #
while True:
    # TEST FOR INPUTS
    events = pygame.event.get()
    for event in events:
        if event.type == QUIT:  # noqa: F405
            pygame.quit()
            sys.exit()
    #___Run only while game is active___#
        if game_var.game_start:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    P1.jump()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    P1.cancel_jump()

    display.surface.blit(background, (0,0))

    if not game_var.game_start:
        title_scene()
        
    if game_var.game_start:
        '''IF PLAYER JUMPS HIGHER, make screen go higher
        move platforms, clouds and coins accordingly'''
        if P1.rect.top <= display.HEIGHT/3:
            P1.pos.y += abs(P1.vel.y)
            for plat in platforms:
                plat.rect.y += abs(P1.vel.y)
                if plat.rect.top > (display.HEIGHT-32):
                    plat.kill()
            for cloud in clouds:
                cloud.rect.y += abs(P1.vel.y)
                if cloud.rect.top > display.HEIGHT:
                    cloud.kill()
            for coin in coins:
                coin.rect.y += abs(P1.vel.y)
                if coin.rect.top >= display.HEIGHT:
                    coin.kill()

        #END GAME IF PLAYER FALLS BELOW SCREEN
        if P1.rect.top > display.HEIGHT:
            if game_var.game_start and not game_var.game_over:
                for entity in all_sprites:
                    entity.kill()
                pygame.mixer.Sound('assets/down.ogg').play()
                set_hi_score(game_var.score)
                game_var.game_over = True       
        
        if game_var.game_over:
            game_over_scene()
                
        if not game_var.game_over:
            P1.update()
            plat_gen()
            cloud_gen()
            
            draw_in_order()
        
            game_hud()

    pygame.display.update()
    timers.FramePerSec.tick(timers.FPS)