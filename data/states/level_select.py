import pygame as pg

from .. import tools, prepare
from ..components.labels import ButtonGroup
from ..components.hud import NumberLabel, MaskedButton


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


class LevelSelectScreen(tools._State):
    def __init__(self):
        super(LevelSelectScreen, self).__init__()
        self.make_bg()
        self.title = Icon(prepare.GFX["text_select_level"],
                              (prepare.SCREEN_RECT.centerx, 50))

    def make_bg(self):
        bg_tile = prepare.GFX["bg_blue"]
        self.bg = pg.Surface(prepare.SCREEN_SIZE)
        for x in range(0, prepare.SCREEN_SIZE[0], bg_tile.get_width()):
            for y in range(0, prepare.SCREEN_SIZE[1], bg_tile.get_height()):
                self.bg.blit(bg_tile, (x, y))

    def make_level_buttons(self):
        self.buttons = ButtonGroup()
        if not self.player.info["scores"]:
            self.player.info["scores"][1] = 0
        levels = sorted(list(self.player.info["scores"].keys()))
        cx = 90
        cy = 160
        for n in levels:
            label = NumberLabel(int(n), (0, 0))
            MaskedButton(label.image, (cx, cy), self.start_level, [n], self.buttons)
            cx += 120
            if cx > 1200:
                cx = 90
                cy += 120

    def start_level(self, level_num):
        self.player.info["level"] = level_num
        self.done = True
        self.next = "LEVEL_START"

    def startup(self, persistent):
        self.persist = persistent
        self.player = self.persist["player"]
        self.crosshair = self.persist["crosshair"]
        self.crosshair.setVisibility(True)
        self.animations = pg.sprite.Group()
        self.icons = pg.sprite.Group()
        self.make_level_buttons()

    def get_event(self, event):
        if event.type == pg.KEYUP:
            self.quit = True
        self.buttons.get_event(event)

    def update(self, dt):
        self.crosshair.update()
        self.buttons.update(dt, self.crosshair.rect.center)

    def draw(self, surface):
        surface.blit(self.bg, (0, 0))
        self.title.draw(surface)
        self.buttons.draw(surface)
        self.crosshair.draw(surface)
