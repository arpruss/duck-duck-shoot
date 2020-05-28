import pygame as pg

from .. import tools, prepare
from ..components.level import GalleryLevel
from ..components.curtain import Curtains
from ..components.hud import HUD


class Gameplay(tools._State):
    def __init__(self):
        super(Gameplay, self).__init__()
        self.level = None
        self.started = False

    def make_level(self):
        self.level = GalleryLevel(self.crosshair, self.player)
        self.curtains = Curtains(prepare.SCREEN_RECT.midbottom,
                                         prepare.SCREEN_SIZE, 80)
        self.hud = HUD(self.level)

    def startup(self, persistent):
        self.persist = persistent
        self.player = self.persist["player"]
        self.crosshair = self.persist["crosshair"]
        self.crosshair.setVisible(False)
        if self.level is None or self.level.done:
            self.make_level()
            pg.mixer.music.load(prepare.MUSIC["RollUp"])
            pg.mixer.music.set_volume(.3)
            pg.mixer.music.play()
            self.curtains.reset()
            self.curtains.open()
            self.started = False

    def get_event(self,event):
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYUP:
            if event.key == pg.K_ESCAPE:
                self.quit = True
            elif event.key == pg.K_r:
                self.done = True
                self.level.done = True
                pg.mixer.music.stop()
                self.next = "LEVEL_START"
        self.level.get_event(event)

    def update(self, dt):
        self.level.update(dt)
        self.curtains.update(dt)
        self.hud.update(dt, self.level.gun)
        if self.level.done:
            self.done = True
            self.next = "COUNT_UP"
            self.hud.reload_notification.active = False
            self.persist["level"] = self.level
            self.persist["curtains"] = self.curtains
            self.persist["hud"] = self.hud

    def draw(self, surf):
        surface = pg.Surface(prepare.SCREEN_SIZE)
        self.level.draw(surface)
        self.curtains.draw(surface)
        self.hud.draw(surface)
        self.crosshair.draw(surface)
        surf.blit(surface, (0, 0))
