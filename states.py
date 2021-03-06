import sfml as sf

from actors import *
from drawables import *
from constants import *

class State:
    PREVIOUS_STATE = "previous"

    def __init__(self, window):
        self.has_ended = False
        self.window = window

class IntroState(State):
    def __init__(self, window):
        State.__init__(self, window)
        self.sprite = sf.Sprite(sf.Texture.from_file("greeting.png"))
        self.view = sf.View()
        self.view.reset(sf.Rectangle((0, 0), (WIDTH, HEIGHT)))

    def step(self, dt):
        for event in self.window.events:
            if type(event) == sf.KeyEvent and event.pressed:
                self.has_ended = True
                self.next_state = GameState

    def draw(self):
        self.window.view = self.view
        self.window.draw(self.sprite)

class ExitState(State):
    def __init__(self, window):
        State.__init__(self, window)
        self.sprite = sf.Sprite(sf.Texture.from_file("exitmodus.png"))
        self.view = sf.View()
        self.view.reset(sf.Rectangle((0, 0), (WIDTH, HEIGHT)))

    def step(self, dt):
        for event in self.window.events:
            if type(event) == sf.KeyEvent and event.pressed:
                if event.code == sf.Keyboard.ESCAPE:
                    self.has_ended = True
                    self.next_state = State.PREVIOUS_STATE
                elif event.code == sf.Keyboard.RETURN:
                    self.has_ended = True
                    self.next_state = None

    def draw(self):
        self.window.view = self.view
        self.window.draw(self.sprite)


class GameWonState(State):
    def __init__(self, window):
        State.__init__(self, window)
        self.sprite = sf.Sprite(sf.Texture.from_file("WinMessage.png"))
        self.view = sf.View()
        self.view.reset(sf.Rectangle((0, 0), (WIDTH, HEIGHT)))

    def draw(self):
        self.window.view = self.view
        self.window.draw(self.sprite)

    def step(self, dt):
        for event in self.window.events:
            if type(event) == sf.KeyEvent and event.pressed:
                if event.code == sf.Keyboard.ESCAPE:
                    self.has_ended = True
                    self.next_state = None
                elif event.code == sf.Keyboard.RETURN:
                    self.has_ended = True
                    self.next_state = GameState


class GameOverState(State):
    def __init__(self, window):
        State.__init__(self, window)
        self.sprite = sf.Sprite(sf.Texture.from_file("endtext.png"))
        self.view = sf.View()
        self.view.reset(sf.Rectangle((0, 0), (WIDTH, HEIGHT)))

    def step(self, dt):
        for event in self.window.events:
            if type(event) == sf.KeyEvent and event.pressed:
                if event.code == sf.Keyboard.ESCAPE:
                    self.has_ended = True
                    self.next_state = None
                elif event.code == sf.Keyboard.RETURN:
                    self.has_ended = True
                    self.next_state = GameState

    def draw(self):
        self.window.view = self.view
        self.window.draw(self.sprite)

class GameState(State):
    def __init__(self, window):
        State.__init__(self, window)

        #self.debug = []

        self.busses = []
        self.creatures = []
        self.lives = []

        self.player = Player(WIDTH / 2, HEIGHT / 2)

        for i in range (0, random.randint(MIN_GRUES, MAX_GRUES)):
            creature = Grue(*random_point_not_near(self.player.position))
            #print("New Grue at (%s)" % (creature.position))
            self.creatures.append(creature)

        for i in range(0, random.randint(MIN_HEALS, MAX_HEALS)):
            heal = Lives(random.randrange(0, MAP_WIDTH),
                    random.randrange(0, MAP_HEIGHT))
            self.lives.append(heal)

        self.background = sf.Sprite(sf.Texture.from_file("map2.png"))
        self.view = sf.View()
        self.view.reset(sf.Rectangle((0, 0), (WIDTH, HEIGHT)))
        self.window.view = self.view

        self.overlay = Overlay(self.player)
        self.dark_overlay = Overlay(self.player, dark=True)

        self.life_point_display = PointDisplay(sf.Rectangle(
            (10, 10), (100, 10)), self.player.health, sf.Color.RED)
        self.stamina_display = PointDisplay(sf.Rectangle((WIDTH - 60 -10, 10), (60, 10)),
                self.player.max_stamina, sf.Color.GREEN)

        self.boss_time = sf.Clock()
        self.run_timer = sf.Clock()
        self.treasure_time = sf.Clock()
        self.stamina_regeneration_timer = sf.Clock()

        self.is_running = False
        self.is_dark = False
        self.has_boss = False
        self.has_treasure = False

    def step(self, dt):
        #self.debug = []

        #self.debug.append("(dt=%i/16 ms)" % dt) 

        if not self.has_treasure and self.treasure_time.elapsed_time >= sf.seconds(120):
            self.treasure = Treasure(*random_point_not_near(self.player.position))
            self.boss = Boss(*random_point_not_near(self.player.position))
            self.creatures.append(self.boss)
            sound.boss1.play()

            #print("Treasure spawned at %s" % self.treasure.position)
            self.has_treasure = True

        if self.has_treasure and self.treasure.win_condition(self.player):
            self.has_ended = True
            self.next_state = GameWonState

        for c in self.creatures:
            if c.collides_with(self.player):
                self.creatures.remove(c)
                c.bite(self.player)
                if self.player.health <= 0:
                    self.has_ended = True
                    self.next_state = GameOverState

        for h in self.lives:
            if h.collides_with(self.player):
                self.lives.remove(h)
                h.heal(self.player)

        def exhaust():
            self.is_running = False
            self.player.stamina -= 1
            if self.player.stamina <= 0:
                sound.exhausted.play()
            self.stamina_regeneration_timer.restart()

        for event in self.window.events:
            if type(event) is sf.CloseEvent \
                    or (type(event) is sf.KeyEvent \
                    and event.pressed and event.code == sf.Keyboard.ESCAPE):
                self.next_state = ExitState
                self.has_ended = True
            elif type(event) is sf.KeyEvent and event.pressed \
                    and event.code == sf.Keyboard.X:
                self.is_dark = not self.is_dark
            elif type(event) is sf.KeyEvent and event.code == sf.Keyboard.L_SHIFT:
                if event.pressed and not self.is_running:
                    self.is_running = True
                    self.run_timer.restart()
                elif event.released and self.is_running:
                    exhaust()

        if self.is_running and self.run_timer.elapsed_time >= sf.seconds(1):
            exhaust()

        #if self.is_running:
        #    self.debug.append("sprint (" + str(self.run_timer.elapsed_time.seconds) + ")")

        if self.player.stamina > 0:
            delta = self.player_movement_vector(self.player)
        else:
            delta = sf.Vector2()

        view_delta = sf.Vector2()
        if self.player.position.x > WIDTH / 2 \
                and self.player.position.x < MAP_WIDTH - WIDTH / 2:
                    view_delta += (delta.x, 0)
        if self.player.position.y > HEIGHT / 2 \
                and self.player.position.y < MAP_HEIGHT - HEIGHT / 2:
                    view_delta += (0, delta.y)

        #self.debug.append("dr: %s" % delta)
        self.player.move(delta, dt)

        sf.Listener.set_position((self.player.position.x,
            self.player.position.y, 0))
        self.view.move(view_delta.x * dt, view_delta.y * dt)

        #self.debug.append("Pos: %s" % self.player.position)

        #Monster movement
        for creature in self.creatures:
            creature.step(self.player, self.is_dark, dt)
            creature.sound_tick()

        if self.stamina_regeneration_timer.elapsed_time >= sf.seconds(5) \
                and self.player.stamina < self.player.max_stamina:
            if self.player.stamina < 0:
                self.player.stamina = 0
            self.player.stamina += 1
            self.stamina_regeneration_timer.restart()

        self.life_point_display.points = self.player.health
        self.stamina_display.points = self.player.stamina

    def draw(self):
        self.window.view = self.view

        self.window.draw(self.background)
        self.window.draw(self.player)
        for creature in self.creatures:
            self.window.draw(creature)
        for heal in self.lives:
            self.window.draw(heal)
        if self.has_treasure:
            self.window.draw(self.treasure)

        if self.is_dark:
            self.window.draw(self.dark_overlay)
        else:
            self.window.draw(self.overlay)

        self.window.view = self.window.default_view

        text = sf.Text("Find the treasure!")
        text.color = sf.Color.YELLOW
        text.position = (0, HEIGHT - 20)
        text.character_size = 12
        if self.has_treasure: self.window.draw(text)

        self.window.draw(self.life_point_display)
        self.window.draw(self.stamina_display)

    def player_movement_vector(self, player):
        delta = sf.Vector2()
        if sf.Keyboard.is_key_pressed(sf.Keyboard.LEFT) \
                and player.position.x > 0:
                    delta += (-1,0)
        elif sf.Keyboard.is_key_pressed(sf.Keyboard.RIGHT) \
                and player.position.x + player.size.x < MAP_WIDTH:
                    delta += (1,0)
        if sf.Keyboard.is_key_pressed(sf.Keyboard.UP) \
                and player.position.y > 0:
                    delta += (0,-1)
        elif sf.Keyboard.is_key_pressed(sf.Keyboard.DOWN) \
                and player.position.y + player.size.y < MAP_HEIGHT:
                    delta += (0,1)
        delta = normalize(delta)

        if self.is_running:
            delta *= 8
        else:
            delta *= 2

        return delta

