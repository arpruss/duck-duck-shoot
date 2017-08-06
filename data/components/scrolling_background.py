import pygame as pg

from .. import prepare


class ScrollingBackground(pg.sprite.DirtySprite):
    def __init__(self, image, bottomleft, width, speed,
                      bob_amount, bob_speed, *groups):
        super(ScrollingBackground, self).__init__(*groups)
        w, h = image.get_size()
        self.scroll_width = w
        self.view_rect = pg.Rect(0, 0, width, h)
        num = ((width + w) // w) + 1
        base = pg.Surface((num * w, h)).convert_alpha()
        base.fill((0,0,0,0))
        for x in range(num):
            base.blit(image, (x * w, 0))
        self.base_image = base
        self.base_rect = self.base_image.get_rect()
        self.rect = pg.Rect((bottomleft[0], bottomleft[1] - h), (width, h))
        self.layer = self.rect.bottom
        self.view_rect.right = self.base_rect.right
        self.scroll_offset = 0
        self.speed = speed
        self.bob_offset = 0
        self.bob_amount = bob_amount
        self.bob_speed = bob_speed
        self.bob_direction = 1
        self.initial_top = self.rect.top
        self.update(0)

    def update(self, dt):
        self.scroll_offset += self.speed * dt
        self.view_rect.left -= int(self.scroll_offset)
        self.scroll_offset -= int(self.scroll_offset)
        if self.view_rect.right < self.base_rect.right - self.scroll_width:
            self.view_rect.right += self.scroll_width
        self.image = self.base_image.subsurface(self.view_rect)

        self.bob_offset += self.bob_speed * dt
        while int(self.bob_offset):
            self.rect.top += int(self.bob_offset) * self.bob_direction
            self.bob_offset -= int(self.bob_offset)
            if self.rect.top >= self.initial_top + self.bob_amount:
                self.bob_direction *= -1
            elif self.rect.top <= self.initial_top - self.bob_amount:
                self.bob_direction *= -1

    def draw(self, surface):
        surface.blit(self.image, self.rect)