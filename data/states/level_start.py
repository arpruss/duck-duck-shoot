import pygame as pg

from .. import tools, prepare
from ..components.animation import Task
from ..components.curtain import Curtains
from ..components.hud import MaskedButton, StarStrip


class LevelStart(tools._State):
    def __init__(self):
        super(LevelStart, self).__init__()
        sr = prepare.SCREEN_RECT
        self.curtains = Curtains(sr.midbottom, sr.size, 80)
        img = prepare.GFX["bg_wood"]
        self.bench = pg.Surface((sr.width, img.get_height()))
        self.bench_rect = self.bench.get_rect(bottomleft=sr.bottomleft)
        for x in range(0, self.bench_rect.w, img.get_width()):
            self.bench.blit(img, (x, 0))
        self.play_button = MaskedButton(prepare.GFX["forward_button"],
                                                      (640, 500), self.start, [])

    def startup(self, persistent):
        sr = prepare.SCREEN_RECT
        self.persist = persistent
        self.player = self.persist["player"]
        self.crosshair = self.persist["crosshair"]
        level_num = self.player.info["level"]
        self.animations = pg.sprite.Group()
        title = prepare.GFX["text_level"]
        title_nums = [prepare.GFX["text_green_{}".format(n)] for n in str(level_num)]
        space = 16
        tw, th = title.get_size()
        total_w = tw + space + sum((x.get_width() for x in title_nums))
        self.title = pg.Surface((total_w, th)).convert_alpha()
        self.title.fill((0,0,0,0))
        self.title.blit(title, (0, 0))
        left = tw + space
        for title_num in title_nums:
            self.title.blit(title_num, (left, 0))
            left += title_num.get_width()
        self.title_rect = self.title.get_rect(midtop=(sr.centerx, 50))

        num_stars = self.player.info["stars"].get(level_num, 0)
        self.star_strip = StarStrip((sr.centerx, 260))
        self.star_strip.make_image(num_stars)
        self.star_strip.active = True

    def get_event(self, event):
        if event.type == pg.KEYUP:
            if event.key == pg.K_ESCAPE:
                self.quit = True
        elif event.type == pg.MOUSEBUTTONUP:
            self.start()
        self.play_button.get_event(event)

    def start(self):
        task = Task(self.leave_state, 250)
        self.animations.add(task)

    def leave_state(self):
        self.done = True
        self.next = "GAMEPLAY"

    def update(self, dt):
        self.animations.update(dt)
        self.crosshair.update()
        self.play_button.update(dt, self.crosshair.rect.center)

    def draw(self, surface):
        surface.blit(self.bench, self.bench_rect)
        self.curtains.draw(surface)
        surface.blit(self.title, self.title_rect)
        self.star_strip.draw(surface)
        self.play_button.draw(surface)
        self.crosshair.draw(surface)