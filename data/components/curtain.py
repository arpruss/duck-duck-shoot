import pygame as pg

from .. import prepare
from ..components.animation import Animation


class CurtainPanel(pg.sprite.DirtySprite):
    def __init__(self, bottomleft, *groups):
        super(CurtainPanel, self).__init__(*groups)
        left, bottom = bottomleft
        frill = prepare.GFX["curtain_straight"]
        frill_w, frill_h = frill.get_size()
        fabric = prepare.GFX["bg_red"]
        fabric_rect = fabric.get_rect()
        num, rem = divmod(bottom - frill_h, fabric_rect.h)
        if rem:
            num += 1
        h = (num * fabric_rect.h) + frill_h

        surf = pg.Surface((frill_w, h)).convert_alpha()
        surf.fill((0,0,0,0))
        surf.blit(frill, (0, h - frill_h))
        fabric_rect.bottom = h - frill_h
        for x in range(num):
            surf.blit(fabric, fabric_rect)
            fabric_rect.top -= fabric_rect.h
        self.image = surf
        self.rect = self.image.get_rect(bottomleft=bottomleft)
        self.original_topleft = self.rect.topleft

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Curtains(object):
    def __init__(self, midbottom, screen_size, side_margin, *groups):
        curtain_w = prepare.GFX["bg_red"].get_width()
        sw, sh = screen_size
        self.panels = pg.sprite.Group()
        self.left_panels = pg.sprite.Group()
        self.right_panels = pg.sprite.Group()

        half_w = (sw // 2) + 1
        num, rem = divmod(half_w, curtain_w)
        if rem:
            num += 1
        right, bottom = midbottom
        for x in range(num):
            c = CurtainPanel((right - (curtain_w * (x + 1)), bottom),
                                   self.left_panels, self.panels, *groups)
        left, bottom = midbottom
        for y in range(num):
            CurtainPanel((left + (y * curtain_w), bottom),
                              self.right_panels, self.panels, *groups)
        self.scroll_amount = midbottom[0] - side_margin
        self.scroll_time = 3000
        self.animations = pg.sprite.Group()
        valence = prepare.GFX["curtain_straight"]
        vw, vh = valence.get_size()
        self.valence = pg.Surface((screen_size[0], vh)).convert_alpha()
        self.valence.fill((0,0,0,0))
        for x in range(0, screen_size[0], vw):
            self.valence.blit(valence, (x, 0))

    def reset(self):
        for p in self.panels:
            p.rect.topleft = p.original_topleft

    def open(self):
        for left_p in self.left_panels:
            new_x = left_p.rect.x - self.scroll_amount
            ani = Animation(x=new_x, duration=self.scroll_time,
                                  round_values=True)
            ani.start(left_p.rect)
            self.animations.add(ani)

        for right_p in self.right_panels:
            new_x = right_p.rect.x + self.scroll_amount
            ani = Animation(x=new_x, duration=self.scroll_time)
            ani.start(right_p.rect)
            self.animations.add(ani)

    def close(self):
        for p in self.panels:
            ani = Animation(x=p.original_topleft[0], duration=self.scroll_time,
                                  round_values=True)
            ani.start(p.rect)
            self.animations.add(ani)

    def update(self, dt):
        self.animations.update(dt)

    def draw(self, surface):
        self.panels.draw(surface)
        surface.blit(self.valence, (0, 0))
