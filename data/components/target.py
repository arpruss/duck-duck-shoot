from math import pi, degrees

import pygame as pg

from .. import prepare
from ..components.angles import project
from ..components.animation import Animation

POINT_VALUES = {
    "duck": 1,
    "orange duck": 50,
    "bullseye": 5,
    "colored bullseye": 25}


class BrokenTarget(pg.sprite.DirtySprite):
    def __init__(self, image, center, layer, *groups):
        super(BrokenTarget, self).__init__(*groups)
        self.image= image
        self.rect = self.image.get_rect(center=center)
        self.pos = self.rect.center
        self.layer = layer
        self.speed = .4
        self.fall_limit = self.pos[1] + 100

    def update(self, dt):
        move = self.speed * dt
        self.pos = self.pos[0], self.pos[1] + move
        self.rect.center = self.pos
        if self.rect.centery >= self.fall_limit:
            self.kill()



class Target(pg.sprite.DirtySprite):
    def __init__(self, target_type, target_image, stick_image,
                      broken_stick_image, stick_anchor,
                      scroll_speed, layer, *groups):
        super(Target, self).__init__(*groups)
        self.target_type = target_type
        self.broken_stick = broken_stick_image
        self.target_rect = target_image.get_rect()
        self.target_mask = pg.mask.from_surface(target_image)
        w, h = stick_image.get_size()
        self.stick_length = h
        self.stick_anchor_x, self.stick_anchor_y = stick_anchor
        self.stick_angle = 0
        self.scroll_speed = scroll_speed
        self.make_base_image(target_image, stick_image, broken_stick_image)
        self.target_image = pg.Surface(self.rect.size).convert_alpha()
        self.target_image.fill((0,0,0,0))
        self.target_image.blit(target_image, (0, 0))
        self.layer = layer
        self.angle = self.start_angle = .5 * pi
        self.rotation_direction = 1

        self.original_anchor = stick_anchor
        self.bob_amount = 64
        self.bob_time = 750
        self.animations = pg.sprite.Group()
        self.done = False

    def make_base_image(self, target_image, stick_image, broken_stick_image):
        tw, th = target_image.get_size()
        sw, sh =  stick_image.get_size()
        w = max(tw, sw)
        h = (sh + (th // 2)) * 2
        base = pg.Surface((w, h)).convert_alpha()
        base.fill((0,0,0,0))
        base_rect = base.get_rect()
        broken = base.copy()
        r = stick_image.get_rect(midbottom=base_rect.center)
        base.blit(stick_image, r)
        r2 = broken_stick_image.get_rect(midbottom=r.midbottom)
        broken.blit(broken_stick_image, r2)
        t_rect = target_image.get_rect(midtop=base_rect.midtop)
        base.blit(target_image, t_rect)
        self.base_image = base
        self.image = self.base_image
        self.broken_base_image = broken
        self.rect = self.image.get_rect(center=self.get_anchor())

    def get_anchor(self):
        return self.stick_anchor_x, self.stick_anchor_y

    def rotate(self, amount):
        self.angle += amount * self.rotation_direction
        if (self.angle < .1 * pi) or (self.angle > .9 * pi):
            self.rotation_direction *= -1
        self.image = pg.transform.rotate(
                    self.base_image, degrees(self.angle - self.start_angle))
        self.target_mask = pg.mask.from_surface(self.image, 0)
        self.rect = self.image.get_rect(center=self.get_anchor())

    def ascend(self):
        new_y = self.original_anchor[1] - self.bob_amount
        ani = Animation(stick_anchor_y=new_y,
                               duration=self.bob_time, round_values=True)
        ani.start(self)
        ani.callback = self.descend
        self.animations.add(ani)

    def descend(self):
        new_y = self.original_anchor[1] + self.bob_amount
        ani = Animation(stick_anchor_y=new_y,
                               duration=self.bob_time, round_values=True)
        ani.start(self)
        ani.callback = self.ascend
        self.animations.add(ani)

    def score(self, all_sprites):
        prepare.SFX["bb-hit2"].play()
        self.done  = True
        self.base_image = self.broken_base_image
        rot_target = pg.transform.rotate(
                    self.target_image, degrees(self.angle - self.start_angle))
        BrokenTarget(rot_target, self.get_anchor(), self.layer - 1, all_sprites)
        self.rotate(0)

    def scroll(self, dt):
        self.stick_anchor_x = self.stick_anchor_x + (self.scroll_speed * dt)

    def update(self, dt):
        self.animations.update(dt)
        self.scroll(dt)
        self.rect.center = self.get_anchor()
        self.target_rect.center = project(self.get_anchor(),
                                                     self.angle, self.stick_length)
        if self.stick_anchor_x > prepare.SCREEN_SIZE[0] + 100:
            self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class YellowDuck(Target):
    def __init__(self, stick_anchor, layer, *groups):
        super(YellowDuck, self).__init__("duck", prepare.GFX["duck_yellow"],
                                                     prepare.GFX["stick_wood"],
                                                     prepare.GFX["stick_wood_broken"],
                                                     stick_anchor, .15, layer, *groups)

    def update(self, dt):
        self.rotate(.001 * dt)
        super(YellowDuck, self).update(dt)


class FastYellowDuck(Target):
    def __init__(self, stick_anchor, layer, *groups):
        super(FastYellowDuck, self).__init__("duck", prepare.GFX["duck_yellow"],
                                                           prepare.GFX["stick_wood"],
                                                           prepare.GFX["stick_wood_broken"],
                                                           stick_anchor, .3, layer, *groups)


class BobbingBullseye(Target):
    def __init__(self, stick_anchor, layer, *groups):
        super(BobbingBullseye, self).__init__("bullseye", prepare.GFX["target_red2"],
                                                            prepare.GFX["stick_metal"],
                                                            prepare.GFX["stick_metal_broken"],
                                                            stick_anchor, .35, layer, *groups)
        self.animations = pg.sprite.Group()
        self.ascend()


class ColoredBullseye(Target):
    def __init__(self, stick_anchor, layer, *groups):
        super(ColoredBullseye, self).__init__("colored bullseye", prepare.GFX["target_colored"],
                                                           prepare.GFX["stick_metal"],
                                                           prepare.GFX["stick_metal_broken"],
                                                           stick_anchor, .5, layer, *groups)


class OrangeDuck(Target):
    def __init__(self, stick_anchor,  layer, *groups):
        super(OrangeDuck, self).__init__("orange duck", prepare.GFX["duck_l'orange"],
                                                      prepare.GFX["stick_wood"],
                                                      prepare.GFX["stick_wood_broken"],
                                                      stick_anchor, .6, layer, *groups)
