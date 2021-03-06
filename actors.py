import random

import sfml as sf

from constants import *
from helpers import *
import sound

class Actor(sf.Drawable):
    def __init__(self):
        sf.Drawable.__init__(self)

        self.sound_rarity = 0
        self.sprite = sf.CircleShape()

    def move(self, dr, dt):
        #print("Move actor by %s" % str(dr))
        #print(self.sprite.position)
        self.sprite.position += dr * dt
        #print(self.sprite.position)

    def draw(self, target, states):
        target.draw(self.sprite, states)

    @property
    def position(self):
        return self.sprite.position

    @position.setter
    def position(self, pos):
        self.sprite.position = pos

    @property
    def size(self):
        try:
            return self.sprite.size
        except AttributeError:
            return self.sprite.texture.size

    def collides_with(self, object):
        r1 = collision_rectangle(self)
        r2 = collision_rectangle(object)
        if ((r1.right < r2.left) or (r2.right < r1.left) or (r1.bottom < r2.top) \
                or (r2.bottom < r1.top)):
            return False
        else:
            return True

    def sound_tick(self):
        if random.randint(0, self.sound_rarity) != 0:
            return
        try:
            #print("sound tick")
            self.play_sound()
        except AttributeError:
            pass

class Player(Actor):
    def __init__(self, x, y):
        Actor.__init__(self)
        player = sf.Texture.from_file("player.png")
        self.sprite = sf.Sprite(player)
        self.position = (x, y)

        self.max_health = 5
        self.health = self.max_health
        self.max_stamina = 4
        self.stamina = self.max_stamina

    def draw(self, target, states):
        target.draw(self.sprite, states)

class Bus(Actor):
    def __init__(self, x, y, start_number):
        Actor.__init__(self)

        self.start_number = start_number

        self.sprite = sf.RectangleShape()
        self.sprite.size = (50, 50)
        self.sprite.outline_color = sf.Color.BLUE
        self.sprite.outline_thickness = 2
        self.position = (x, y)

    def draw(self, target, states):
        target.draw(self.sprite, states)

    def move(self):
        if (self.position.x > 342 and self.position.y > 0):
            super(Bus, self).move(0, 1)

    def get_number(self):
        return self.start_number

class Monster(Actor):
    def __init__(self):
        Actor.__init__(self)

        self.direction = random_unit_vector()
        self.direction_timer = sf.Clock()

    def step(self, player, is_dark, dt):
        if is_dark:
            range = 60
        else:
            range = 180
        if dist(self.position, player.position) <= range and not is_dark:
            self.hunt_player(player, dt)
        else:
            self.move_randomly(dt)

    def move_randomly(self, dt):
        if self.direction_timer.elapsed_time > sf.seconds(5) \
                or not MAP_RECT.contains(self.position + (self.direction * self.speed * 10)):
            self.direction = random_unit_vector()
            self.direction_timer.restart()

        self.move(self.direction * self.speed, dt)

    def hunt_player(self, player, dt):
        player_direction = player.position - self.position
        delta = (player_direction / norm(player_direction)) * self.speed * 2

        self.move(delta, dt)

    def bite(self, player):
        if self.collides_with(player):
            player.health -= self.damage

class Grue(Monster):
    def __init__(self, x, y):
        Monster.__init__(self)
        small_monster = sf.Texture.from_file("small_monster.png")
        self.sprite = sf.Sprite(small_monster)
        self.sprite.position = (x, y)

        self.speed = 1
        self.damage = 1
        self.sound_rarity = 4800

    def bite(self, player):
        sound.roar.play()
        #print("played sound")
        super(Grue, self).bite(player)

    def play_sound(self):
        if sound.grue.status != sf.SoundSource.PLAYING:
            sound.grue.position = vector2to3(self.position)
            sound.grue.attenuation = 150
            sound.grue.play()

class Boss(Monster):
    def __init__(self, x, y):
        Monster.__init__(self)
        big_monster = sf.Texture.from_file("big_monster.png")
        self.sprite = sf.Sprite(big_monster)
        self.sprite.position = (x, y)
        self.sound_rarity = 1200

        self.speed = 1.10
        self.damage = 5

    def step(self, player, is_dark, dt):
        self.hunt_player(player, dt)

    def play_sound(self):
        #print("play boss")
        snd = random.choice([sound.boss1, sound.boss2])
        if snd.status != sf.SoundSource.PLAYING:
            snd.position = vector2to3(self.postion)
            snd.play()

class Lives(Actor):
    def __init__(self, x, y):
        Actor.__init__(self)
        dagger = sf.Texture.from_file("Dagger.png")
        self.sprite = sf.Sprite(dagger)
        self.health = 1
        self.sprite.position = (x, y)

    def heal(self, player):
        if player.health < player.max_health:
            player.health += self.health
            sound.heal.play()

class Treasure(Actor):
    def __init__(self, x, y):
        Actor.__init__(self)
        self.sprite = sf.Sprite(sf.Texture.from_file("treasure.png"))
        self.sprite.position = (x, y)

    def win_condition(self, player):
        return self.collides_with(player)

