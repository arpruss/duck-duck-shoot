import os
import json

import pygame as pg

from .. import prepare
from ..components.scrolling_background import ScrollingBackground
from ..components.crosshair import Crosshair
from ..components.target import YellowDuck, FastYellowDuck, BobbingBullseye, ColoredBullseye, OrangeDuck, POINT_VALUES
from ..components.gun import Gun


STICK_HEIGHT = 120        
        
        
class GalleryLevel(object):
    def __init__(self, crosshair, player):
        self.player = player
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.scrollers = pg.sprite.Group()
        self.ducks = pg.sprite.Group()
        self.sky = pg.sprite.Group()
        self.target_types = {
                "yellow duck": [YellowDuck, (self.ducks, self.all_sprites)],
                "fast yellow duck": [FastYellowDuck, (self.ducks, self.all_sprites)],
                "orange duck": [OrangeDuck, (self.ducks, self.all_sprites)],
                "bobbing bullseye": [BobbingBullseye, (self.ducks, self.all_sprites)],
                "colored bullseye": [ColoredBullseye, (self.ducks, self.all_sprites)]
                }
        
        
        self.load_level_targets()
        self.rows = {}
        w = prepare.SCREEN_SIZE[0]
        row_info = [
                ["6", "water1", (0, 835), w, .16, 16, .05, [self.scrollers, self.all_sprites]],
                ["5", "water2", (0, 735), w, .22, 16, .05,  [self.scrollers, self.all_sprites]],
                ["4", "water1", (0, 635), w, .27, 16, .05,  [self.scrollers, self.all_sprites]],
                ["3", "water2", (0, 535), w, .3, 16, .05,  [self.scrollers, self.all_sprites]],
                ["2", "grass2", (0, 445), w, 0, 0, 0, [self.all_sprites]],
                ["1", "grass3", (0, 350), w, 0, 0, 0,  [self.all_sprites]],
                ["bench", "bg_wood", (0, 945), w, 0, 0, 0,  [self.all_sprites]],
                ["sky2", "bg_blue", (0, 256), w, 0, 0, 0,  [self.sky]],
                ["sky1", "bg_blue", (0, 512), w, 0, 0, 0, [self.sky]]
                ]
        for name, bg_image, bottomleft, width, scroll_speed, bob_amount, bob_speed, groups in row_info:
            s = ScrollingBackground(prepare.GFX[bg_image], bottomleft, width, scroll_speed, bob_amount, bob_speed, *groups)
            if self.all_sprites in groups:
                self.rows[name] = GalleryRow(s, s.layer)
            
        self.crosshair = crosshair
        self.gun = Gun(self.crosshair, self.player.info["max bullets"])
        self.total_time = 0
        self.done  = False
        self.started = False
        self.max_score = 0

    def load_level_targets(self):
        level_num = self.player.info["level"]
        p = os.path.join("resources", "levels", "{}.json".format(level_num))
        with open(p, "r") as f:
            target_list = json.load(f)
        self.target_list = target_list
        
    def add_target(self, row_name, target_type):   
        row = self.rows[row_name]
        row.add_target(target_type, self.target_types, self)
        

    def update(self, dt):
        self.total_time += dt
        self.all_sprites.update(dt)
        for s in self.all_sprites:
            self.all_sprites.change_layer(s, s.layer)
        self.crosshair.update()
        for t in self.target_list:
            row_name, target_type, timestamp = t
            if self.total_time >= timestamp:
                self.add_target(row_name, target_type)
                self.target_list.remove(t)
        if not self.target_list and not [x for x in self.ducks if not x.done]:        
            self.done = True

    def get_event(self, event):
        rows = sorted(self.rows.values(), key=lambda x: x.layer, reverse=True)
        self.gun.get_event(event, self.ducks, rows, self.all_sprites)

    def draw(self, surface):
        surface.fill(pg.Color("black"))
        self.sky.draw(surface)
        self.all_sprites.draw(surface)


class GalleryRow(object):
    def __init__(self, background, layer):
        self.bg = background
        self.layer = layer
        self.targets = pg.sprite.Group()

    def add_target(self, target_type, target_types, level):
        klass, groups = target_types[target_type]
        d = klass((-50, self.layer - STICK_HEIGHT), self.layer, self.targets, *groups)
        level.max_score += POINT_VALUES[d.target_type]
