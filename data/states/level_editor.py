import os
from collections import OrderedDict
import json

import pygame as pg

from .. import tools, prepare
from ..components.labels import Button, ButtonGroup, Label
from ..components.target import YellowDuck, FastYellowDuck, BobbingBullseye, ColoredBullseye, OrangeDuck

TARGET_TYPES = {
        "yellow duck": YellowDuck,
        "fast yellow duck": FastYellowDuck,
        "orange duck": OrangeDuck,
        "bobbing bullseye": BobbingBullseye,
        "colored bullseye": ColoredBullseye
        }


class Row(object):
    def __init__(self, topleft, layer):
        self.rect = pg.Rect(topleft, (prepare.SCREEN_SIZE[0], 100))
        self.targets = []
        self.layer = layer

    def add_target(self, target_type, name, timestamp, targets):
        t = target_type((-50, self.rect.bottom), self.layer, targets)
        t.name = name
        t.timestamp = timestamp

    def draw(self, surface):
        pg.draw.rect(surface, pg.Color("white"), self.rect, 1)


class LevelEditor(tools._State):
    def __init__(self):
        super(LevelEditor, self).__init__()
        self.make_rows()
        self.make_buttons()
        self.selected_row = self.rows[1]
        self.targets = pg.sprite.Group()
        self.timestamp = 0
        self.time_label = Label("{}".format(self.timestamp), {"midtop": prepare.SCREEN_RECT.midtop})
        self.num = 0
        self.num_label = Label("{}".format(self.num), {"topright": prepare.SCREEN_RECT.topright})
        
    def make_rows(self):
        self.rows = OrderedDict()
        left, top = (0, 150)
        for x in range(1, 7):
            self.rows[x] = Row((left, top), x)
            top += 80
            
    def make_buttons(self):
        self.buttons = ButtonGroup()
        left, top = 50, 10
        for name in TARGET_TYPES:
            t = TARGET_TYPES[name]((0,0), 1)
            img = t.target_image.subsurface(t.target_rect)
            size = img.get_size()
            Button((left, top), self.buttons, idle_image=img, button_size=size, call=self.add_target, args=(TARGET_TYPES[name], name))
            left += 100

    def add_target(self, args):
        target_class, name = args
        self.selected_row.add_target(target_class, name, self.timestamp, self.targets)

    def load(self):
        p = os.path.join("resources", "levels", "{}.json".format(self.num))
        with open(p, "r") as f:
            targets = json.load(f)
        by_time = sorted(targets, key=lambda x: x[2])
        last = self.timestamp
        for layer, name, timestamp in by_time:
            #self.timestamp = timestamp
            self.selected_row = self.rows[int(layer)]
            diff = timestamp - self.timestamp
            if diff:
                self.scroll(diff)
            self.add_target((TARGET_TYPES[name], name)) 
            
        
    def save(self):
        target_list = [(str(t.layer), t.name, t.timestamp) for t in self.targets]
        with open("wip_level.json", "w") as f:
            json.dump(target_list, f)
            

    def startup(self, persistent):
        self.persist = persistent
        pg.mouse.set_visible(True)
        
    def get_event(self, event):
        if event.type == pg.KEYUP:
            if event.key == pg.K_ESCAPE:
                self.quit = True
                self.save()
            elif event.key == pg.K_d:
                self.scroll(100)
            elif event.key == pg.K_a:
                self.scroll(-100)
            elif event.key == pg.K_UP:
                self.num += 1
                self.num_label.set_text("{}".format(self.num))
            elif event.key == pg.K_DOWN:
                self.num -= 1
                self.num_label.set_text("{}".format(self.num))
            elif event.key == pg.K_l:
                self.load()
            elif event.key == pg.K_LEFTBRACKET:
                self.scroll(-1000)
            elif event.key == pg.K_RIGHTBRACKET:
                self.scroll(1000)
        elif event.type == pg.MOUSEBUTTONUP:
            if event.button == 3:
                for t in self.targets:
                    if t.rect.collidepoint(event.pos):
                        t.kill()
            elif event.button == 1:
                for r in self.rows.values():
                    if r.rect.collidepoint(event.pos):
                        self.selected_row = r
        self.buttons.get_event(event)
        

    def scroll(self, amount):
        self.timestamp += amount
        for t in self.targets:
            t.scroll(amount)
            t.rect.center = t.get_anchor()
        self.time_label.set_text("{}".format(self.timestamp))
        
    def update(self, dt):
        self.buttons.update(pg.mouse.get_pos())
        keys = pg.key.get_pressed()
        if keys[pg.K_RIGHT]:
            self.scroll(100)
        if keys[pg.K_LEFT]:
            self.scroll(-100)
            
    def draw(self, surface):
        surface.fill(pg.Color("black"))
        surface.fill(pg.Color("gray5"), self.selected_row.rect)
        for row in self.rows.values():
            row.draw(surface)
        for t in sorted(self.targets, key=lambda x: x.get_anchor()[1]):
            t.draw(surface)
        self.buttons.draw(surface)
        self.time_label.draw(surface)
        self.num_label.draw(surface)
        

