import pygame as pg

from .. import tools, prepare
from ..components.hud import MaskedButton
from ..components.labels import ButtonGroup
from ..components.animation import Task


class Icon(pg.sprite.Sprite):
    def __init__(self, image, center, *groups):
        super(Icon, self).__init__(*groups)
        self.image = pg.Surface(image.get_size())
        self.image.fill((60, 158, 215))
        self.image.set_colorkey((60, 158, 215))
        self.image.blit(image, (0, 0))
        self.rect = self.image.get_rect(center=center)
        self.alpha = 255

    def draw(self, surface):
        surface.blit(self.image, self.rect)



class MenuScreen(tools._State):
    def __init__(self):
        super(MenuScreen, self).__init__()
        self.animations = pg.sprite.Group()
        self.icons = pg.sprite.Group()
        self.make_bg()
        self.make_buttons()

    def make_bg(self):
        bg_tile = prepare.GFX["bg_blue"]
        self.bg = pg.Surface(prepare.SCREEN_SIZE)
        for x in range(0, prepare.SCREEN_SIZE[0], bg_tile.get_width()):
            for y in range(0, prepare.SCREEN_SIZE[1], bg_tile.get_height()):
                self.bg.blit(bg_tile, (x, y))

    def make_buttons(self):
        self.buttons = ButtonGroup()
        MaskedButton(prepare.GFX["button_help"],
                            (300, 300), self.help, [], self.buttons)
        MaskedButton(prepare.GFX["button_level_select"],
                            (640, 300), self.level_select, [], self.buttons)
        MaskedButton(prepare.GFX["button_high_scores"],
                            (980, 300), self.high_scores, [], self.buttons)

    def help(self):
        t = Task(self.leave_state, 250, args=("HELP",))
        self.animations.add(t)

    def level_select(self):
        t = Task(self.leave_state, 250, args=("LEVEL_SELECT",))
        self.animations.add(t)

    def high_scores(self):
        pass

    def leave_state(self, next_state):
        self.done = True
        self.next = next_state

    def startup(self, persistent):
        self.persist = persistent
        self.crosshair = self.persist["crosshair"]

    def get_event(self, event):
        if event.type == pg.KEYUP:
            if event.key == pg.K_ESCAPE:
                self.quit = True
        self.buttons.get_event(event)

    def update(self, dt):
        self.animations.update(dt)
        self.crosshair.update()
        self.buttons.update(dt, self.crosshair.rect.center)

    def draw(self, surface):
        surface.blit(self.bg, (0, 0))
        self.buttons.draw(surface)
        self.crosshair.draw(surface)