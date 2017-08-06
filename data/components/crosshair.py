import pygame as pg

from .. import prepare


class Crosshair(object):
    def __init__(self, image):
        self.pos = pg.mouse.get_pos()
        self.image = image
        self.rect = self.image.get_rect(center=self.pos)

    def update(self):
        self.pos = pg.mouse.get_pos()
        self.rect.center = self.pos

    def draw(self, surface):
        surface.blit(self.image, self.rect)