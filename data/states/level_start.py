import pygame as pg

from .. import tools, prepare

class LevelStart(tools._State):
    def __init__(self,
        self.curtains = Curtains(prepare.SCREEN_RECT.midbottom, prepare.SCREEN_SIZE, 80)
    
    def startup(self, persistent):
        self.persist = persistent
        self.player = self.persist["player"]
        self.crosshair = self.persist["crosshair"]
        
    def get_event(self, event):
        self.buttons.get_event(event)
        
    def update(self, dt):
        pass
        
    def draw(self, surface):
        self.curtains.draw(surface)
        self.crosshair.draw(surface)