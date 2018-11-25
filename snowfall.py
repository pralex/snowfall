import pygame
import random
import sys
import time


MAX_X = 1366
MAX_Y = 768

SNOW_SIZE = 64

counter = 0
shots = 0

levels = [
     dict(snow=20, shots=25, min_size=64, max_size=64, timeout=25000),
     dict(snow=55, shots=55, min_size=32, max_size=64, timeout=120000),
     dict(snow=100, shots=95, min_size=16, max_size=64, timeout=180000),
     dict(snow=1000, shots=1000, min_size=16, max_size=64, timeout=300000),
]

# create a bunch of events
shot_event = pygame.USEREVENT + 1
autoshot_event = pygame.USEREVENT + 2
timeout_event = pygame.USEREVENT + 3

trigger = False
stop_time = None


class Snow:

    def __init__(self, x, y):
        global counter

        counter += 1
        self.id = str(counter)
        self.x = x
        self.y = y
        self.speed = random.randint(1, 3)
        self.img_num = random.randint(1, 5)
        self.image_filename = "image%s.png" % str(self.img_num)
        self.image = pygame.image.load(self.image_filename).convert_alpha()
        self.size = random.randint(levels[current_level].get('min_size'), levels[current_level].get('max_size'))
        self.image = pygame.transform.scale(self.image, (self.size, self.size))
        if self.img_num == 5 and random.randint(0, 1):
                self.image = pygame.transform.flip(self.image, random.randint(0, 1), random.randint(0, 1))

    def move_snow(self):
        self.y += self.size//16 + 1
        if self.y > MAX_Y:
            self.y = -SNOW_SIZE
        i = random.randint(1, 3)
        if i == 1:
            self.x += 1
        elif i == 2:
            self.x -= 1
        if self.x > MAX_X:
            self.x = -self.size
        elif self.x < -self.size:
            self.x = MAX_X

    def draw_snow(self):
        screen.blit(self.image, (self.x, self.y))

    def shot(self, x, y):
        return (x in range(self.x, self.x + self.size)) and (y in range(self.y, self.y + self.size))


def initialize():
    global shots, snowfall, stop_time

    shots = levels[current_level].get('shots')
    for i in range(levels[current_level].get('snow')):
        xx = random.randint(0, MAX_X)
        yy = random.randint(0, MAX_Y)
        snowfall[i] = Snow(xx, yy)
    stop_time = pygame.time.get_ticks() + levels[current_level].get('timeout')


def check_for_exit():
    global snowfall, shots, trigger, shot_sound

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pygame.event.post(pygame.event.Event(shot_event, {}))
        elif event.type == shot_event:
            if pygame.mouse.get_pressed()[0]:
                if shots > 0:
                    shots -= 1
                    shot_sound.play()
                    x, y = pygame.mouse.get_pos()
                    shooten = []
                    for key in snowfall.keys():
                        if snowfall[key].shot(x, y):
                            shooten.append(key)
                    for snow_id in shooten:
                        snowfall.pop(snow_id)

                pygame.time.set_timer(shot_event, 300)


def draw_scope():
    x, y = pygame.mouse.get_pos()
    screen.blit(scope_image, (x-100, y-100))


if __name__ == '__main__':

    pygame.init()
    screen = pygame.display.set_mode((MAX_X, MAX_Y), pygame.FULLSCREEN)
    font1 = pygame.font.SysFont("Arial", 36)
    font2 = pygame.font.SysFont("Arial", 72)
    font3 = pygame.font.SysFont("Arial", 144)

    scope_image = pygame.image.load('scope_2x.png').convert_alpha()
    scope_image = pygame.transform.scale(scope_image, (200, 200))
    bg_color = (0, 0, 20)
    snowfall = {}
    current_level = 0
    initialize()
    # pygame.mixer.music.load('snowfall.mp3')
    # pygame.mixer.music.play()
    shot_sound = pygame.mixer.Sound("shotgun.ogg")
    pygame.mouse.set_visible(False)

    while True:
        screen.fill(bg_color)
        check_for_exit()
        if len(snowfall) == 0:
            current_level += 1
            if current_level == len(levels):
                result = font3.render("YOU WIN", True, (0, 128, 0))
                break
            else:
                initialize()
        else:
            if shots > 0:
                for snow in snowfall.keys():
                    snowfall[snow].move_snow()
                    snowfall[snow].draw_snow()
                draw_scope()
                screen.blit(font1.render("SNOW: " + str(len(snowfall)), True, (0, 128, 0)), (0, 0))
                screen.blit(font1.render("SHOTS: " + str(shots), True, (0, 128, 0)), (0, 50))
                curr_time = (stop_time - pygame.time.get_ticks())//1000
                if curr_time <= 0:
                    result = font3.render("GAME OVER", True, (128, 0, 0))
                    break
                screen.blit(font2.render("TIME: %02d:%02d" % (curr_time//60, curr_time % 60),
                                         True, (255, 255, 0)), (1030, 0))
                lvl = font2.render("LEVEL " + str(current_level+1), True, (0, 128, 0))
                screen.blit(lvl, ((MAX_X - lvl.get_height()) // 2, 0))
            else:
                result = font3.render("GAME OVER", True, (128, 0, 0))
                break

        time.sleep(0.02)
#        rect = pygame.draw.rect(screen, (0, 0, 128), ((MAX_X - 500) // 2, (MAX_Y - 200) // 2, 500, 200))
        pygame.display.flip()

    coords = ((MAX_X - result.get_width()) // 2, (MAX_Y - result.get_height()) // 2)
    screen.blit(result, coords)
    pygame.display.flip()
    pygame.time.wait(2000)
